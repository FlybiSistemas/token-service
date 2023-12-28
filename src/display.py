class Display:  
    def __init__(self, root, tkinter, func, master=None):
        self.root = root
        self.func = func

        self.fontePadrao = ("Arial", "10")
        self.primeiroContainer = tkinter.Frame(master)
        self.primeiroContainer["pady"] = 10
        self.primeiroContainer.pack()

        self.segundoContainer = tkinter.Frame(master)
        self.segundoContainer["padx"] = 20
        self.segundoContainer.pack()

        self.terceiroContainer = tkinter.Frame(master)
        self.terceiroContainer["padx"] = 20
        self.terceiroContainer.pack()

        self.quartoContainer = tkinter.Frame(master)
        self.quartoContainer["pady"] = 20
        self.quartoContainer.pack()

        self.titulo = tkinter.Label(self.primeiroContainer, text="Chave para instalação:")
        self.titulo["font"] = ("Arial", "10", "bold")
        self.titulo.pack()

        self.senhaLabel = tkinter.Label(self.terceiroContainer, text="Token", font=self.fontePadrao)
        self.senhaLabel.pack(side=tkinter.LEFT)

        self.senha = tkinter.Entry(self.terceiroContainer)
        self.senha["width"] = 30
        self.senha["font"] = self.fontePadrao
        self.senha.pack(side=tkinter.LEFT)

        self.autenticar = tkinter.Button(self.quartoContainer)
        self.autenticar["text"] = "Instalar"
        self.autenticar["font"] = ("Calibri", "8")
        self.autenticar["width"] = 12
        self.autenticar["command"] = self.instalarParaEFD
        self.autenticar.pack(side=tkinter.LEFT, padx=5)

        self.mensagem = tkinter.Label(self.quartoContainer, text="", font=self.fontePadrao)
        self.mensagem.pack()

    def instalarParaEFD(self):
        global root
        senhaTemp = self.senha.get()
        self.senha.delete(0, 'end')
        self.func(senhaTemp)
        

