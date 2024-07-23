from computer import Computer


def main():
    print("Fetching Computer... ", end='')
    computer = Computer()
    computer.request_all_infos_computer()
    print("done.")


if __name__ == '__main__':
    main()
