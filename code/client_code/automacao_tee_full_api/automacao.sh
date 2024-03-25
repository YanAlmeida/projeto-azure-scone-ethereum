#!/bin/bash

# Defina as variáveis com os endereços dos seus nós TEE e Ganache
TEE_NODES=("40.79.58.243")
NON_PUBLIC_NODE="10.0.1.6"

GANACHE_NODE="3.17.175.207"

export BLOCKCHAIN_ADDRESS="http://${GANACHE_NODE}:8545"

CONTAINERS_HASHES_TEE=("untrusted" "tee" "nginx")

BATCH_SIZES=(1 10 50 100 200 150 200 250 250)
CLIENT_NUMBERS=(1 1 1 1 1 2 2 2 4)
FILE_SIZES=("1kb" "5kb" "10kb" "50kb" "100kb", "1mb", "5mb", "10mb")

eval $(ssh-agent -s)
ssh-add /root/.ssh/id_rsa


# Função para parar os containers do nó TEE
stop_tee_containers() {
    for node in "${TEE_NODES[@]}"; do
        ssh -o StrictHostKeyChecking=no ubuntu@$node "sudo docker rm --force \$(sudo docker ps -q)"
    done
    # ssh -A -o StrictHostKeyChecking=no ubuntu@${TEE_NODES[0]} ssh -o StrictHostKeyChecking=no ubuntu@$NON_PUBLIC_NODE "sudo docker rm --force \$(sudo docker ps -q)"
}

# Função para reiniciar o container Ganache
restart_ganache_container() {
    ssh -o StrictHostKeyChecking=no ubuntu@$GANACHE_NODE "sudo docker rm --force \$(sudo docker ps -q)"
    sleep 1
    ssh -o StrictHostKeyChecking=no ubuntu@$GANACHE_NODE sudo docker run -d -p 8545:8545 yanalmeida91/mockchain:latest
}


run_untrusted_container() {
    for i in "${!TEE_NODES[@]}"; do
        node="${TEE_NODES[i]}"
        ssh -o StrictHostKeyChecking=no ubuntu@$node "sudo docker run -d --name untrusted --network=\"host\" \
                                                            -e BLOCKCHAIN_ADDRESS=\"${BLOCKCHAIN_ADDRESS}\" \
                                                            -e CONTRACT_ABI='[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_machine","type":"address"},{"indexed":false,"internalType":"uint256","name":"_value","type":"uint256"}],"name":"ReturnUInt","type":"event"},{"inputs":[],"name":"connectMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"connectedMachines","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"disconnectMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"disconnectedMachines","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getJobs","outputs":[{"internalType":"uint256[]","name":"jobIds","type":"uint256[]"},{"internalType":"string[]","name":"fileUrls","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"_jobsIds","type":"uint256[]"}],"name":"getJobsMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getJobsMachineView","outputs":[{"internalType":"uint256[]","name":"jobsIds","type":"uint256[]"},{"internalType":"string[]","name":"fileUrls","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_jobId","type":"uint256"}],"name":"getResult","outputs":[{"internalType":"uint256","name":"charCount","type":"uint256"},{"internalType":"string","name":"message","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"heartBeat","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobProcessingInfo","outputs":[{"internalType":"uint256","name":"waitingTimestamp","type":"uint256"},{"internalType":"uint256","name":"processingTimestamp","type":"uint256"},{"internalType":"uint256","name":"currentStatus","type":"uint256"},{"internalType":"address","name":"responsibleMachine","type":"address"},{"internalType":"uint256","name":"indexInJobs","type":"uint256"},{"internalType":"uint256","name":"indexInMachine","type":"uint256"},{"internalType":"uint256","name":"processedTimestamp","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobProcessingMaxTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobUpdateInterval","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobWaitingMaxTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsPerAddress","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsPerId","outputs":[{"internalType":"uint256","name":"jobId","type":"uint256"},{"internalType":"string","name":"fileUrl","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"resultsPerJobId","outputs":[{"internalType":"uint256","name":"jobId","type":"uint256"},{"internalType":"uint256","name":"charCount","type":"uint256"},{"internalType":"string","name":"message","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"url","type":"string"}],"name":"submitJob","outputs":[{"internalType":"uint256","name":"_jobId","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"_jobsIds","type":"uint256[]"},{"internalType":"uint256[]","name":"_charCounts","type":"uint256[]"},{"internalType":"string[]","name":"_messages","type":"string[]"}],"name":"submitResults","outputs":[],"stateMutability":"nonpayable","type":"function"}]' \
                                                            -e CONTRACT_ADDRESS=\"0x5b92A0289CBeBacC143842122bC3c5B78e5584FB\" \
                                                            -e ACCOUNT_INDEX=\"${i}\" -e POLL_INTERVAL=\"${1}\" -e LIMIT_JOBS=\"${2}\" \
                                                            yanalmeida91/sgx-untrusted-blockchain-pull:latest"
    done
    # ssh -A -o StrictHostKeyChecking=no ubuntu@${TEE_NODES[0]} ssh -o StrictHostKeyChecking=no ubuntu@$NON_PUBLIC_NODE "sudo docker run -d --name untrusted --network=\"host\" \
    #                                                                                                                     -e BLOCKCHAIN_ADDRESS=\"${BLOCKCHAIN_ADDRESS}\" \
    #                                                                                                                     -e CONTRACT_ABI='[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_machine","type":"address"},{"indexed":false,"internalType":"uint256","name":"_value","type":"uint256"}],"name":"ReturnUInt","type":"event"},{"inputs":[],"name":"connectMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"connectedMachines","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"disconnectMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"disconnectedMachines","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getJobs","outputs":[{"internalType":"uint256[]","name":"jobIds","type":"uint256[]"},{"internalType":"string[]","name":"fileUrls","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"_jobsIds","type":"uint256[]"}],"name":"getJobsMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getJobsMachineView","outputs":[{"internalType":"uint256[]","name":"jobsIds","type":"uint256[]"},{"internalType":"string[]","name":"fileUrls","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_jobId","type":"uint256"}],"name":"getResult","outputs":[{"internalType":"uint256","name":"charCount","type":"uint256"},{"internalType":"string","name":"message","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"heartBeat","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobProcessingInfo","outputs":[{"internalType":"uint256","name":"waitingTimestamp","type":"uint256"},{"internalType":"uint256","name":"processingTimestamp","type":"uint256"},{"internalType":"uint256","name":"currentStatus","type":"uint256"},{"internalType":"address","name":"responsibleMachine","type":"address"},{"internalType":"uint256","name":"indexInJobs","type":"uint256"},{"internalType":"uint256","name":"indexInMachine","type":"uint256"},{"internalType":"uint256","name":"processedTimestamp","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobProcessingMaxTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobUpdateInterval","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobWaitingMaxTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsPerAddress","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsPerId","outputs":[{"internalType":"uint256","name":"jobId","type":"uint256"},{"internalType":"string","name":"fileUrl","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"resultsPerJobId","outputs":[{"internalType":"uint256","name":"jobId","type":"uint256"},{"internalType":"uint256","name":"charCount","type":"uint256"},{"internalType":"string","name":"message","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"url","type":"string"}],"name":"submitJob","outputs":[{"internalType":"uint256","name":"_jobId","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"_jobsIds","type":"uint256[]"},{"internalType":"uint256[]","name":"_charCounts","type":"uint256[]"},{"internalType":"string[]","name":"_messages","type":"string[]"}],"name":"submitResults","outputs":[],"stateMutability":"nonpayable","type":"function"}]' \
    #                                                                                                                     -e CONTRACT_ADDRESS=\"0x5b92A0289CBeBacC143842122bC3c5B78e5584FB\" \
    #                                                                                                                     -e ACCOUNT_INDEX=\"3\" -e POLL_INTERVAL=\"${1}\" -e LIMIT_JOBS=\"${2}\" \
    #                                                                                                                     yanalmeida91/sgx-untrusted-blockchain-pull:latest"
}

run_tee_container() {
    for node in "${TEE_NODES[@]}"; do
        ssh -o StrictHostKeyChecking=no ubuntu@$node "sudo docker run -d --name tee --device=/dev/sgx_enclave -v /var/run/aesmd/aesm.socket:/var/run/aesmd/aesm.socket -p 9090:9090 gsc-yanalmeida91/sgx-blockchain-pull:latest"
    done
    # ssh -A -o StrictHostKeyChecking=no ubuntu@${TEE_NODES[0]} ssh -o StrictHostKeyChecking=no ubuntu@$NON_PUBLIC_NODE "sudo docker run -d --name tee --device=/dev/sgx_enclave -v /var/run/aesmd/aesm.socket:/var/run/aesmd/aesm.socket -p 9090:9090 gsc-yanalmeida91/sgx-blockchain-pull:latest"
}

run_nginx_container() {
    for node in "${TEE_NODES[@]}"; do
        ssh -o StrictHostKeyChecking=no ubuntu@$node "sudo docker run -d --name nginx -p 8080:80 yanalmeida91/nginx-file-repo:latest"
    done
    # ssh -A -o StrictHostKeyChecking=no ubuntu@${TEE_NODES[0]} ssh -o StrictHostKeyChecking=no ubuntu@$NON_PUBLIC_NODE "sudo docker run -d --name nginx -p 8080:80 yanalmeida91/nginx-file-repo:latest"
}

# Função para reiniciar os containers TEE
restart_tee_containers() {
    run_tee_container
    run_untrusted_container $1 $2
    run_nginx_container
}

run_test() {
    export BATCH_SIZE=$1

    RPS=$(echo "scale=1; $1 * $2" | bc)

    # Se o resultado terminar com '.0', então queremos remover a parte decimal
    if [[ $RPS == *.0 ]]; then
        RPS="${RPS%.*}"
    # Caso contrário, se começar com '.', adicionamos um '0' à esquerda
    elif [[ $RPS == .* ]]; then
        RPS="0$RPS"
    fi

    locust -f main.py --headless -u $2 --spawn-rate $2 --host "http://127.0.0.1:8080/output_$3.pdf?${RPS}RPS" --run-time 5m
}

# Execute o Locust test
for i in "${!BATCH_SIZES[@]}"; do
    for test in "${FILE_SIZES[@]}"; do

        echo "Parando TEE"
        stop_tee_containers

        echo "Reiniciando blockchain"
        restart_ganache_container

        sleep 5

        echo "Reiniciando TEE"
        restart_tee_containers 1 1

        while ! nc -z ${TEE_NODES[0]} 9090; do
            echo "Service at ${TEE_NODES[0]}:9090 is not available yet. Waiting for 5 seconds..."
            sleep 5
        done

        echo "Criando diretorio para dados do teste"
        RPS=$(echo "scale=1; ${BATCH_SIZES[i]} * ${CLIENT_NUMBERS[i]}" | bc)
        # Se o resultado terminar com '.0', então queremos remover a parte decimal
        if [[ $RPS == *.0 ]]; then
            RPS="${RPS%.*}"
        # Caso contrário, se começar com '.', adicionamos um '0' à esquerda
        elif [[ $RPS == .* ]]; then
            RPS="0$RPS"
        fi

        export TEST_IDENTIFIER="${test}-${RPS}RPS"
        mkdir "/tmp/${test}-${RPS}RPS"

        echo "Executando teste ${test} para BATCH=${BATCH_SIZES[i]} e CLIENTS=${CLIENT_NUMBERS[i]}"
        run_test "${BATCH_SIZES[i]}" "${CLIENT_NUMBERS[i]}" "${test}"

        echo "Coletando resultados"
        python3 coletar_dados.py

    done
done
# Coleta os dados dos testes

echo "Teste e reinício automatizado concluído!"
