// SPDX-License-Identifier: MIT 
pragma solidity ^0.8.0;

contract smartContract {

    // ------------------ DEFINIÇÃO DE EVENTOS DE RETORNO / EVENTOS DE DISPARO ------------------ //
    event ReturnUInt(address indexed _machine, uint _value);

    // ------------------ DEFINIÇÃO DE ESTRUTURAS E VARIÁVEIS ------------------ //

    // Definição de estrutura para dados referentes aos nós
    struct AddressInfo {
        bool isConnected;
        uint timestamp;
        uint connectedIndex;
        uint disconnectedIndex;
    }

    // Definição da estrutura do Job
    struct Job {
        uint jobId;
        string fileUrl;
    }

    // Definição de estrutura para dados referentes ao processamento do job
    struct JobProcessingInfo {
        uint waitingTimestamp;
        uint processingTimestamp;
        uint currentStatus;
        address responsibleMachine;
        uint indexInJobs;
        uint indexInMachine;
        uint processedTimestamp;
    }

    // Definição da estrutura do resultado
    struct Result {
        uint jobId;
        uint charCount;
        string message;
    }

    // Definição de mapping para tracking do processamento do job
    mapping(uint => JobProcessingInfo) public jobProcessingInfo;

    // Definição de mappings e array para acesso aos jobs
    mapping(address => uint[]) public jobsPerAddress;

    mapping(uint => Job) public jobsPerId;
    uint[] public jobs;

    // Definição de mappings e array para acesso aos resultados
    mapping(uint => Result) public resultsPerJobId;


    // Definição de mappings e arrays para controle das máquinas relacionadas ao contrato
    mapping(address => AddressInfo) private addressInfo;

    address[] public connectedMachines;
    address[] public disconnectedMachines;

    // Definição de variável para load balancing
    uint machineIndex = 0;

    // Definição de variáveis para auxílio na criação de Jobs (lastJobId) e na validação de máquinas disponíveis (jobUpdateInterval)
    uint private lastJobId = 0;
    uint public jobUpdateInterval = 20 minutes;

    // Variáveis para auxílio em timeouts
    uint public jobWaitingMaxTime = 10 minutes;
    uint public jobProcessingMaxTime = 10 minutes;

    // ------------------ DEFINIÇÃO DE FUNÇÕES EXTERNAS E PÚBLICAS ------------------ //

    // Função para leitura dos jobs cadastrados (todos)
    function getJobs() external view returns (
        uint[] memory jobIds,
        string[] memory fileUrls
    ){
        uint length = jobs.length;

        // Prepara estruturas para retorno, preenchendo-as com dados dos jobs
        jobIds = new uint[](length);
        fileUrls = new string[](length);

        for (uint i = 0; i < length; i++) {
            Job memory job = jobsPerId[jobs[i]];
            jobIds[i] = job.jobId;
            fileUrls[i] = job.fileUrl;
        }

        return (jobIds, fileUrls);
    }

    // Função para submissão de job
    function submitJob(string calldata url) external returns (uint _jobId) {
        _jobId = lastJobId + 1;
        lastJobId++;
        jobsPerId[_jobId] = Job(_jobId, url);
        jobs.push(_jobId);

        jobProcessingInfo[_jobId].waitingTimestamp = block.timestamp;
        jobProcessingInfo[_jobId].indexInJobs = jobs.length - 1;
        
        uint[] memory jobsToAddress = new uint[](1);
        jobsToAddress[0] = _jobId;

        addressJobs(jobsToAddress);
        
        emit ReturnUInt(msg.sender, _jobId);
        return _jobId;
    }

    // Função para recuperação de jobs para processamento
    function getJobsMachine(uint[] calldata _jobsIds) external{
        // Recupera jobs no mapping "WAITING" para a máquina que realiza a busca
        uint length = _jobsIds.length;

        for (uint i = 0; i < length; i++) {
            jobProcessingInfo[_jobsIds[i]].processingTimestamp = block.timestamp;
            jobProcessingInfo[_jobsIds[i]].currentStatus = 2;            
        }
    }

    // Função para retorno de resultado referente ao job solicitado
    function getJobsMachineView() external view returns(
        uint[] memory jobsIds,
        string[] memory fileUrls
    ) {
        uint length = jobsPerAddress[msg.sender].length;

        jobsIds = new uint[](length);
        fileUrls = new string[](length);

        for (uint i=0; i < length; i++){
            Job memory job = jobsPerId[jobsPerAddress[msg.sender][i]];
            if(jobProcessingInfo[job.jobId].currentStatus == 1 && jobProcessingInfo[job.jobId].responsibleMachine == msg.sender){
                jobsIds[i] = (job.jobId);
                fileUrls[i] = (job.fileUrl);
            }
        }
        return (jobsIds, fileUrls);
    }

    // Função para submissão de resultados de jobs
    function submitResults(uint[] calldata _jobsIds, uint[] calldata _charCounts, string[] calldata _messages) external {
        uint length = _jobsIds.length;

        // Percorre lista de jobsIds e os retira do mapping "PROCESSING" e inclui no mapping "PROCESSED"
        for(uint i = 0; i < length; i++){
            uint _jobId = _jobsIds[i];
            uint _charCount = _charCounts[i];
            string memory _message = _messages[i];

            resultsPerJobId[_jobId] = Result(_jobId, _charCount, _message);
            jobProcessingInfo[_jobId].processedTimestamp = block.timestamp;

            // Remove o Job
            removeJob(_jobId);
        }

    }

    // Função para retorno de resultado referente ao job solicitado
    function getResult(uint _jobId) external view returns(
        uint charCount,
        string memory message
    ) {
        return (resultsPerJobId[_jobId].charCount, resultsPerJobId[_jobId].message);
    }


    // Função para que nó seja reconhecido como disponível para alocação de jobs (conexão de nó)
    function connectMachine() external {
        require(!isMachineConnected(msg.sender), "Machine already registered");

        if (addressInfo[msg.sender].timestamp != 0) {
            // Remove da lista de desconectados
            disconnectedMachines[addressInfo[msg.sender].disconnectedIndex] = disconnectedMachines[disconnectedMachines.length - 1];
            disconnectedMachines.pop();

            // Atualiza o index do último desconectado, que foi deslocado no processo de remoção
            if(disconnectedMachines.length > 0 && addressInfo[msg.sender].disconnectedIndex < disconnectedMachines.length){
                addressInfo[disconnectedMachines[addressInfo[msg.sender].disconnectedIndex]].disconnectedIndex = addressInfo[msg.sender].disconnectedIndex;
                addressInfo[msg.sender].disconnectedIndex = type(uint).max;  
            }
        }

        // Inclui na lista de conectados
        connectedMachines.push(msg.sender);
        addressInfo[msg.sender] = AddressInfo(true, block.timestamp, connectedMachines.length - 1, type(uint).max);
    }

    // Função para que nó se desconecte do sistema, se tornando indisponível para alocação de jobs
    function disconnectMachine() external {
        updateMachineDisconnected(msg.sender);
    }

    // Função para recebimento de heart beat dos nós
    function heartBeat() external {
        updateMachineTimestamp(msg.sender);
        updateAvailableConnectedMachines();
        redistributeDisconnectedMachinesJobs();
        readdressProcessingJobs();
    }

    // ------------------ DEFINIÇÃO DE FUNÇÕES INTERNAS E PRIVADAS ------------------ //

    function removeJobMachine(uint _jobId) private {

        jobsPerAddress[jobProcessingInfo[_jobId].responsibleMachine][jobProcessingInfo[_jobId].indexInMachine] = jobsPerAddress[jobProcessingInfo[_jobId].responsibleMachine][jobsPerAddress[jobProcessingInfo[_jobId].responsibleMachine].length - 1];
        jobsPerAddress[jobProcessingInfo[_jobId].responsibleMachine].pop();

        if(jobsPerAddress[jobProcessingInfo[_jobId].responsibleMachine].length > 0 && jobProcessingInfo[_jobId].indexInMachine < jobsPerAddress[jobProcessingInfo[_jobId].responsibleMachine].length){
            jobProcessingInfo[jobsPerAddress[jobProcessingInfo[_jobId].responsibleMachine][jobProcessingInfo[_jobId].indexInMachine]].indexInMachine = jobProcessingInfo[_jobId].indexInMachine;
        }

    }

    function removeJob(uint _jobId) private {
        jobs[jobProcessingInfo[_jobId].indexInJobs] = jobs[jobs.length - 1];
        jobs.pop();

        if(jobs.length > 0 && jobProcessingInfo[_jobId].indexInJobs < jobs.length){
            jobProcessingInfo[jobs[jobProcessingInfo[_jobId].indexInJobs]].indexInJobs = jobProcessingInfo[_jobId].indexInJobs;
        }

        removeJobMachine(_jobId);
    }

    // Função para 'retornar' jobs processing há muito tempo ao estado waiting
    function readdressProcessingJobs() private {
        uint lengthJobs = jobs.length;
        uint[] memory readdressJobs = new uint[](1);

        for(uint i = 0; i < lengthJobs; i++){
            uint _jobId = jobs[i];
            if(jobProcessingInfo[_jobId].currentStatus == 2){
                uint processingTimestamp = jobProcessingInfo[_jobId].processingTimestamp;
                uint processingTime = block.timestamp - processingTimestamp;
                if( processingTime > jobProcessingMaxTime){
                    readdressJobs[0] = _jobId;
                    removeJobMachine(_jobId);
                    addressJobs(readdressJobs);
                }
            }

        }
    }

    // Função para distribuição dos jobs entre as máquinas disponíveis utilizando round-robin
    function addressJobs(uint[] memory jobsToAddress) private{
        uint length = jobsToAddress.length;

        if(connectedMachines.length == 0){
            jobsPerAddress[address(0)] = concat(jobsPerAddress[address(0)], jobsToAddress);
        }else{
            for(uint i = 0; i < length; i++){
                uint jobId = jobsToAddress[i];

                if(machineIndex >= connectedMachines.length){
                    machineIndex = 0;
                }
                
                jobsPerAddress[connectedMachines[machineIndex]].push(jobId);

                // Armazena dados do processamento do job
                jobProcessingInfo[jobId].processingTimestamp = 0;
                jobProcessingInfo[jobId].currentStatus = 1;
                jobProcessingInfo[jobId].responsibleMachine = connectedMachines[machineIndex];
                jobProcessingInfo[jobId].indexInMachine = jobsPerAddress[connectedMachines[machineIndex]].length - 1;

                machineIndex++;

            }
        }

    }

    // Função para redistribuir jobs de máquinas desconectadas
    function redistributeDisconnectedMachinesJobs() private {
        uint length = disconnectedMachines.length;

        for(uint i = 0; i < length; i++){
            address disconnectedMachine = disconnectedMachines[i];
            if(jobsPerAddress[disconnectedMachine].length > 0){
                addressJobs(jobsPerAddress[disconnectedMachine]);

                delete jobsPerAddress[disconnectedMachine];
            }
        }

        // Redistribui jobs sem servidor
        if(jobsPerAddress[address(0)].length > 0){
            addressJobs(jobsPerAddress[address(0)]);
            delete jobsPerAddress[address(0)];
        }
    }

    // Função para atualizar estados dos nós
    function updateAvailableConnectedMachines() private {
        uint length = connectedMachines.length;

        for(uint i = length; i > 0; i--){
            address connectedMachine = connectedMachines[i - 1];

            if(!isMachineAvailable(connectedMachine)){
                updateMachineDisconnected(connectedMachine);
            }
        }
    }

    // Função para atualização do timestamp de uma máquina
    function updateMachineTimestamp(address _machine) private{
        require(isMachineConnected(_machine), "Machine not registered");
        addressInfo[_machine].timestamp = block.timestamp;
    }


    // Função para remoção de nó inativo 
    function updateMachineDisconnected(address _machine) private {
        if(isMachineConnected(_machine)){
            // Altera flag 'isConnected'
            addressInfo[_machine].isConnected = false;
            
            // Remove da lista de conectados
            connectedMachines[addressInfo[_machine].connectedIndex] = connectedMachines[connectedMachines.length - 1];
            connectedMachines.pop();

            // Atualiza o index do último conectado, que foi deslocado no processo de remoção
            if(connectedMachines.length > 0 && addressInfo[_machine].connectedIndex < connectedMachines.length){
                addressInfo[connectedMachines[addressInfo[_machine].connectedIndex]].connectedIndex = addressInfo[_machine].connectedIndex;
            }
            addressInfo[_machine].connectedIndex = type(uint).max;

            // Inclui na lista de desconectados
            disconnectedMachines.push(_machine);
            addressInfo[_machine].disconnectedIndex = disconnectedMachines.length - 1;
        }
    }

    // Função para checagem se nó está ativo
    function isMachineConnected(address _machine) private view returns (bool) {
        return addressInfo[_machine].isConnected;
    }

    // Função para checagem de disponibilidade do nó baseado no último heartbeat recebido
    function isMachineAvailable(address _machine) private view returns (bool) {
        return (block.timestamp - addressInfo[_machine].timestamp <= jobUpdateInterval);
    }

    // Função para concatenação de dois arrays
    function concat(uint[] memory arr1, uint[] memory arr2) pure private returns(uint[] memory) {
        uint[] memory result = new uint[](arr1.length + arr2.length);
        
        for (uint i = 0; i < arr1.length; i++) {
            result[i] = arr1[i];
        }
        for (uint j = 0; j < arr2.length; j++) {
            result[arr1.length + j] = arr2[j];
        }
    
        return result;
    }
}