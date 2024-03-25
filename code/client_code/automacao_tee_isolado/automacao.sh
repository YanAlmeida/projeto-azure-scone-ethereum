#!/bin/bash

# Defina as variáveis com os endereços dos seus nós TEE e Ganache
TEE_NODE="40.79.58.243"

CONTAINERS_HASHES_TEE=("tee")

WAIT_TIMES=(1 1 0.5 0.25 0.25 0.33 0.25 0.2 0.2)
CLIENT_NUMBERS=(1 10 25 25 50 100 100 100 100)

FILE_SIZES=("1kb" "5kb" "10kb" "50kb" "100kb" "1mb" "5mb")

eval $(ssh-agent -s)
ssh-add /root/.ssh/id_rsa


# Função para parar os containers do nó TEE
stop_tee_containers() {
    for container_hash in "${CONTAINERS_HASHES_TEE[@]}"; do
        ssh -o StrictHostKeyChecking=no ubuntu@$TEE_NODE sudo docker rm --force $container_hash
    done
}


# Função para reiniciar os containers TEE
restart_tee_containers() {
    ssh -o StrictHostKeyChecking=no ubuntu@$TEE_NODE sudo docker run -d --name tee --device=/dev/sgx_enclave -v /var/run/aesmd/aesm.socket:/var/run/aesmd/aesm.socket -p 9090:9090 gsc-yanalmeida91/sgx-blockchain-pull:latest
}

run_test() {
    export WAIT_TIME=$1
    export TEE_ADDRESS=$4

    RPS=$(echo "scale=1; $2 / $1" | bc)

    # Se o resultado terminar com '.0', então queremos remover a parte decimal
    if [[ $RPS == *.0 ]]; then
        RPS="${RPS%.*}"
    # Caso contrário, se começar com '.', adicionamos um '0' à esquerda
    elif [[ $RPS == .* ]]; then
        RPS="0$RPS"
    fi

    locust -f main.py --headless -u $2 --spawn-rate $2 --host "output_$3.pdf/${RPS}RPS" --run-time 2m30s
}

# Execute o Locust test
for i in "${!WAIT_TIMES[@]}"; do
    for test in "${FILE_SIZES[@]}"; do

        echo "Parando TEE"
        stop_tee_containers

        sleep 1

        echo "Reiniciando TEE"
        restart_tee_containers

        while ! nc -z $TEE_NODE 9090; do
            echo "Service at $TEE_NODE:9090 is not available yet. Waiting for 5 seconds..."
            sleep 5
        done

        echo "Criando diretorio para dados do teste"
        
        RPS=$(echo "scale=1; ${CLIENT_NUMBERS[i]} / ${WAIT_TIMES[i]}" | bc)
        # Se o resultado terminar com '.0', então queremos remover a parte decimal
        if [[ $RPS == *.0 ]]; then
            RPS="${RPS%.*}"
        # Caso contrário, se começar com '.', adicionamos um '0' à esquerda
        elif [[ $RPS == .* ]]; then
            RPS="0$RPS"
        fi
        mkdir "/tmp/${test}-${RPS}RPS"

        echo "Executando teste ${test} para WAIT=${WAIT_TIMES[i]} e CLIENTS=${CLIENT_NUMBERS[i]}"
        run_test "${WAIT_TIMES[i]}" "${CLIENT_NUMBERS[i]}" "${test}" "${TEE_NODE}"

        echo "Coletando resultados"
        python3 coletar_dados.py

    done
done
# Coleta os dados dos testes

echo "Teste e reinício automatizado concluído!"
