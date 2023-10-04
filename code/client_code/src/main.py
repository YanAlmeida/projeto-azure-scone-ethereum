from src.smart_contract import get_contract

if __name__ == '__main__':
    while True:
        user_input = input(
            "Insira o nome do método a executar e seus argumentos, "
            "se houver, separados por vírgula. Para sair, escreva 'SAIR'"
        )

        user_input_array = user_input.split(',')

        method = user_input_array[0]

        if method == "SAIR":
            break

        args = []
        kwargs = {}

        for arg in user_input_array[1:]:
            if "=" in arg:
                arg_splitted = arg.split("=")
                kwargs[arg_splitted[0]] = arg_splitted[1]
            else:
                args.append(arg)

        contract = get_contract()

        print(getattr(contract, method)(*args, **kwargs))
