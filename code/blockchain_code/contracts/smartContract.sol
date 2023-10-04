// SPDX-License-Identifier: MIT 
pragma solidity ^0.8.0;

contract smartContract {

    // ------------------ DEFINIÇÃO DE EVENTOS DE RETORNO / EVENTOS DE DISPARO ------------------ //

    event ReturnJobs(address indexed _machine, uint[] _jobsIds, string[] _filesUrls);
    event ReturnUInt(address indexed _machine, uint _value);
    event NotifyMachines(address indexed _machine);

    // ------------------ DEFINIÇÃO DE ESTRUTURAS E VARIÁVEIS ------------------ //

    // Definição de estrutura para dados referentes aos nós
    struct AddressInfo{
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

    // Definição da estrutura do resultado
    struct Result {
        uint jobId;
        uint charCount;
        string message;
    }

    // Definição de mappings e array para acesso aos jobs
    mapping(address => uint[]) public jobsWAITINGPerAddress;
    mapping(address => uint[]) public jobsPROCESSINGPerAddress;
    mapping(address => uint[]) public jobsPROCESSEDPerAddress;

    mapping(uint => uint) private jobToIndexInProcessing; // Para facilitar remoção de jobs do estado 'processing'
    mapping(uint => Job) public jobsPerId;
    uint[] public jobs;

    // Definição de mappings e array para acesso aos resultados
    mapping(uint => Result) public resultsPerJobId;


    // Definição de mappings e arrays para controle das máquinas relacionadas ao contrato
    mapping(address => AddressInfo) private addressInfo;
    mapping(address => bool) private machineNotified;

    address[] public connectedMachines;
    address[] public disconnectedMachines;

    // Definição de variável para load balancing
    uint machineIndex = 0;

    // Definição de variáveis para auxílio na criação de Jobs (lastJobId) e na validação de máquinas disponíveis (jobUpdateInterval)
    uint private lastJobId = 0;
    uint public jobUpdateInterval = 1 minutes;

    // ------------------ DEFINIÇÃO DE FUNÇÕES EXTERNAS E PÚBLICAS ------------------ //

    // Função para submissão de job
    function submitJob(string calldata url) external returns (uint _jobId) {
        _jobId = lastJobId + 1;
        lastJobId++;
        require(jobsPerId[_jobId].jobId == 0, "Job already exists");
        jobsPerId[_jobId] = Job(_jobId, url);
        jobs.push(_jobId);
        
        uint[] memory jobsToAddress = new uint[](1);
        jobsToAddress[0] = _jobId;

        addressJobs(jobsToAddress);
        
        emit ReturnUInt(msg.sender, _jobId);
        return _jobId;
    }

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

    // Função para recuperação de jobs para processamento
    function getJobsMachine() external returns (
        uint[] memory jobIds,
        string[] memory fileUrls
    ){
        updateMachineTimestamp(msg.sender);

        // Recupera jobs no mapping "WAITING" para a máquina que realiza a busca
        uint[] memory jobsReturn = jobsWAITINGPerAddress[msg.sender];
        uint length = jobsReturn.length;

        // Prepara estruturas para retorno, preenchendo-as com dados dos jobs
        jobIds = new uint[](length);
        fileUrls = new string[](length);

        for (uint i = 0; i < length; i++) {
            Job memory job = jobsPerId[jobsReturn[i]];
            jobIds[i] = job.jobId;
            fileUrls[i] = job.fileUrl;

            // Inclui index do job no array de processamento no mapping "PROCESSING"
            jobToIndexInProcessing[job.jobId] = jobsPROCESSINGPerAddress[msg.sender].length + i;
        }

        // Concatena jobs a retornar no mapping "PROCESSING"    
        jobsPROCESSINGPerAddress[msg.sender] = concat(jobsPROCESSINGPerAddress[msg.sender], jobsReturn);
        delete jobsWAITINGPerAddress[msg.sender];
        
        emit ReturnJobs(msg.sender, jobIds, fileUrls);
        return (jobIds, fileUrls);
    }
    


    // Função para submissão de resultados de jobs
    function submitResults(uint[] calldata _jobsIds, uint[] calldata _charCounts, string[] calldata _messages) external {
        updateMachineTimestamp(msg.sender);
        uint length = _jobsIds.length;

        // Percorre lista de jobsIds e os retira do mapping "PROCESSING" e inclui no mapping "PROCESSED"
        for(uint i = 0; i < length; i++){
            uint _jobId = _jobsIds[i];
            uint _charCount = _charCounts[i];
            string memory _message = _messages[i];

            require(jobsPerId[_jobId].jobId != 0, "Job not found");
            resultsPerJobId[_jobId] = Result(_jobId, _charCount, _message);

            jobsPROCESSEDPerAddress[msg.sender].push(_jobId);
            removeJobFromProcessing(msg.sender, _jobId);
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
            addressInfo[disconnectedMachines[addressInfo[msg.sender].disconnectedIndex]].disconnectedIndex = addressInfo[msg.sender].disconnectedIndex;
            addressInfo[msg.sender].disconnectedIndex = type(uint).max;   
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
    }

    // ------------------ DEFINIÇÃO DE FUNÇÕES INTERNAS E PRIVADAS ------------------ //

    // Função para distribuição dos jobs entre as máquinas disponíveis utilizando round-robin
    function addressJobs(uint[] memory jobsToAddress) private{
        uint length = jobsToAddress.length;

        for(uint i = 0; i < length; i++){
            uint jobId = jobsToAddress[i];

            if(machineIndex == connectedMachines.length){
                machineIndex = 0;
            }
            
            jobsWAITINGPerAddress[connectedMachines[machineIndex]].push(jobId);
            machineNotified[connectedMachines[machineIndex]] = true;
            machineIndex++;
        }

        for(uint i = 0; i < connectedMachines.length; i++){
            if(machineNotified[connectedMachines[i]]){
                emit NotifyMachines(connectedMachines[i]);
                delete machineNotified[connectedMachines[i]];
            }
        }

    }

    // Função para remoção de job do mapping de "PROCESSING"
    function removeJobFromProcessing(address _machine, uint jobIdToRemove) private {
        // Recupera index do job
        uint index = jobToIndexInProcessing[jobIdToRemove];

        // O troca pelo último e remove
        jobsPROCESSINGPerAddress[_machine][index] = jobsPROCESSINGPerAddress[_machine][jobsPROCESSINGPerAddress[_machine].length - 1];
        jobsPROCESSINGPerAddress[_machine].pop();

        // Atualiza mapping de indexes
        jobToIndexInProcessing[jobsPROCESSINGPerAddress[_machine][index]] = index;
        delete jobToIndexInProcessing[jobIdToRemove];

    }

    // Função para redistribuir jobs de máquinas desconectadas
    function redistributeDisconnectedMachinesJobs() private {
        uint length = disconnectedMachines.length;

        for(uint i = 0; i < length; i++){
            address disconnectedMachine = disconnectedMachines[i];

            addressJobs(jobsWAITINGPerAddress[disconnectedMachine]);
            addressJobs(jobsPROCESSINGPerAddress[disconnectedMachine]);

            delete jobsWAITINGPerAddress[disconnectedMachine];
            delete jobsPROCESSINGPerAddress[disconnectedMachine];
        }
    }

    // Função para atualizar estados dos nós
    function updateAvailableConnectedMachines() private {
        uint length = connectedMachines.length;

        for(uint i = 0; i < length; i++){
            address connectedMachine = connectedMachines[i];

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
        // Altera flag 'isConnected'
        addressInfo[_machine].isConnected = false;
        
        // Remove da lista de conectados
        connectedMachines[addressInfo[_machine].connectedIndex] = connectedMachines[connectedMachines.length - 1];
        connectedMachines.pop();

        // Atualiza o index do último conectado, que foi deslocado no processo de remoção
        addressInfo[connectedMachines[addressInfo[_machine].connectedIndex]].connectedIndex = addressInfo[_machine].connectedIndex;
        addressInfo[_machine].connectedIndex = type(uint).max;

        // Inclui na lista de desconectados
        disconnectedMachines.push(_machine);
        addressInfo[_machine].disconnectedIndex = disconnectedMachines.length - 1;
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