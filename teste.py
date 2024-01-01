import winreg
def configure_registry():
    try:
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "bytoken") as bytoken_key:
            winreg.SetValueEx(bytoken_key, "URL Protocol", 0, winreg.REG_SZ, "")

            with winreg.CreateKey(bytoken_key, "shell\\open\\command") as command_key:
                winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, r"C:\Users\JoãoPaulodeMelo\Desktop\teste.exe")

    except Exception as e:
        print(f"Erro ao configurar o registro: {e}")


if __name__ == "__main__":
    configure_registry()
