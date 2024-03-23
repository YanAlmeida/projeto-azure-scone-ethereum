#!/bin/bash

# Defina as variáveis com os endereços dos seus nós TEE e Ganache
TEE_NODES=("40.84.53.153" "40.84.53.48")
NON_PUBLIC_NODE="10.0.1.6"

GANACHE_NODE="18.223.172.239"

export BLOCKCHAIN_ADDRESS="http://${GANACHE_NODE}:8545"

CONTAINERS_HASHES_TEE=("untrusted" "tee" "nginx")

BATCH_SIZES=(5 10 15 20 20 20 20 25)
CLIENT_NUMBERS=(1 1 1 1 2 3 4 4)
FILE_SIZES=("1kb" "10kb" "100kb", "1mb", "5mb", "10mb")

eval $(ssh-agent -s)
ssh-add /root/.ssh/id_rsa


# Função para parar os containers do nó TEE
stop_tee_containers() {
    for node in "${TEE_NODES[@]}"; do
        for container_hash in "${CONTAINERS_HASHES_TEE[@]}"; do
            ssh -o StrictHostKeyChecking=no ubuntu@$node sudo docker stop $container_hash
        done
    done
    for container_hash in "${CONTAINERS_HASHES_TEE[@]}"; do
        ssh -A -o StrictHostKeyChecking=no ubuntu@${TEE_NODES[0]} ssh -o StrictHostKeyChecking=no ubuntu@$NON_PUBLIC_NODE sudo docker stop $container_hash
    done
}

# Função para reiniciar o container Ganache
restart_ganache_container() {
    ssh -o StrictHostKeyChecking=no ubuntu@$GANACHE_NODE "sudo docker rm --force \$(sudo docker ps -q)"
    sleep 1
    ssh -o StrictHostKeyChecking=no ubuntu@$GANACHE_NODE sudo docker run -d -p 8545:8545 yanalmeida91/ganache-smart-contract:latest
}


# Função para reiniciar os containers TEE
restart_tee_containers() {
    for node in "${TEE_NODES[@]}"; do
        for container_hash in "${CONTAINERS_HASHES_TEE[@]}"; do
            ssh -o StrictHostKeyChecking=no ubuntu@$node sudo docker restart $container_hash
        done
    done
    for container_hash in "${CONTAINERS_HASHES_TEE[@]}"; do
        ssh -A -o StrictHostKeyChecking=no ubuntu@${TEE_NODES[0]} ssh -o StrictHostKeyChecking=no ubuntu@$NON_PUBLIC_NODE sudo docker restart $container_hash
    done
}

run_test() {
    export BATCH_SIZE=$1

    RPS=$(echo "scale=1; $1 * $2 / 10" | bc)

    # Se o resultado terminar com '.0', então queremos remover a parte decimal
    if [[ $RPS == *.0 ]]; then
        RPS="${RPS%.*}"
    # Caso contrário, se começar com '.', adicionamos um '0' à esquerda
    elif [[ $RPS == .* ]]; then
        RPS="0$RPS"
    fi

    locust -f main.py --headless -u $2 --host "http://127.0.0.1:8080/output_$3.pdf?${RPS}RPS" --run-time 7m
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
        restart_tee_containers

        while ! nc -z ${TEE_NODE[0]} 9090; do
            echo "Service at ${TEE_NODE[0]}:9090 is not available yet. Waiting for 5 seconds..."
            sleep 5
        done

        echo "Criando diretorio para dados do teste"
        
        RPS=$(echo "scale=1; ${BATCH_SIZES[i]} * ${CLIENT_NUMBERS[i]} / 10" | bc)
        # Se o resultado terminar com '.0', então queremos remover a parte decimal
        if [[ $RPS == *.0 ]]; then
            RPS="${RPS%.*}"
        # Caso contrário, se começar com '.', adicionamos um '0' à esquerda
        elif [[ $RPS == .* ]]; then
            RPS="0$RPS"
        fi
        mkdir "/tmp/${test}-${RPS}RPS"

        echo "Executando teste ${test} para BATCH=${BATCH_SIZES[i]} e CLIENTS=${CLIENT_NUMBERS[i]}"
        run_test "${BATCH_SIZES[i]}" "${CLIENT_NUMBERS[i]}" "${test}"

        echo "Coletando resultados"
        python3 coletar_dados.py

    done
done
# Coleta os dados dos testes

echo "Teste e reinício automatizado concluído!"
