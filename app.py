import os
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog


class ArvoreDiretoriosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Visual de Árvore de Diretórios")
        self.root.geometry("1300x780")
        self.root.configure(bg="#16070c")

        self.pasta_raiz = None
        self.zoom_fator = 1.0
        self.limite_profundidade = tk.IntVar(value=4)

        self.criar_estilo()
        self.criar_interface()

    def criar_estilo(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background="#16070c", borderwidth=0)

        style.configure(
            "TNotebook.Tab",
            background="#3b0f1c",
            foreground="white",
            padding=[22, 10],
            font=("Segoe UI", 10, "bold")
        )

        style.map("TNotebook.Tab", background=[("selected", "#8b1e35")])

        style.configure(
            "Treeview",
            background="#240b12",
            foreground="#f8e9ee",
            fieldbackground="#240b12",
            rowheight=30,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#5c1020",
            foreground="white",
            font=("Segoe UI", 11, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", "#8b1e35")],
            foreground=[("selected", "white")]
        )

    def criar_botao(self, master, texto, comando, cor="#5c1020"):
        return tk.Button(
            master,
            text=texto,
            command=comando,
            bg=cor,
            fg="white",
            activebackground="#9e2642",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=10
        )

    def criar_interface(self):
        topo = tk.Frame(self.root, bg="#3b0f1c", height=86)
        topo.pack(fill="x")

        tk.Label(
            topo,
            text="Árvore Genérica de Diretórios",
            bg="#3b0f1c",
            fg="white",
            font=("Segoe UI", 23, "bold")
        ).pack(side="left", padx=25)

        tk.Label(
            topo,
            text="Gerenciamento, exclusão e visualização gráfica profissional",
            bg="#3b0f1c",
            fg="#e7bdc7",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        self.aba_gerenciador = tk.Frame(self.notebook, bg="#16070c")
        self.aba_grafica = tk.Frame(self.notebook, bg="#16070c")

        self.notebook.add(self.aba_gerenciador, text="Gerenciador")
        self.notebook.add(self.aba_grafica, text="Árvore Gráfica")

        self.criar_aba_gerenciador()
        self.criar_aba_grafica()

    def criar_aba_gerenciador(self):
        menu = tk.Frame(self.aba_gerenciador, bg="#16070c", width=250)
        menu.pack(side="left", fill="y", padx=(0, 20))

        botoes = [
            ("Selecionar Diretório", self.selecionar_diretorio),
            ("Atualizar Árvore", self.atualizar_arvore),
            ("Gerar Árvore Gráfica", self.gerar_arvore_grafica),
            ("Criar Pasta", self.criar_pasta),
            ("Renomear", self.renomear_item),
            ("Excluir Selecionado", self.excluir_item),
            ("Abrir no Explorador", self.abrir_explorador),
            ("Expandir Tudo", self.expandir_tudo),
            ("Recolher Tudo", self.recolher_tudo)
        ]

        for texto, comando in botoes:
            self.criar_botao(menu, texto, comando).pack(fill="x", pady=6)

        self.info = tk.Label(
            menu,
            text="Nenhum diretório selecionado.",
            bg="#16070c",
            fg="#e7bdc7",
            wraplength=230,
            justify="left",
            font=("Segoe UI", 9)
        )
        self.info.pack(pady=20)

        area_arvore = tk.Frame(self.aba_gerenciador, bg="#240b12")
        area_arvore.pack(side="right", fill="both", expand=True)

        self.tree = ttk.Treeview(
            area_arvore,
            columns=("tipo", "caminho"),
            show="tree headings"
        )

        self.tree.heading("#0", text="Nome")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("caminho", text="Caminho")

        self.tree.column("#0", width=330)
        self.tree.column("tipo", width=100, anchor="center")
        self.tree.column("caminho", width=700)

        scroll_y = ttk.Scrollbar(area_arvore, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(area_arvore, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        self.tree.bind("<<TreeviewOpen>>", self.carregar_subpastas)
        self.tree.bind("<<TreeviewSelect>>", self.mostrar_item_selecionado)

    def criar_aba_grafica(self):
        painel = tk.Frame(self.aba_grafica, bg="#16070c")
        painel.pack(fill="x", pady=(0, 12))

        self.criar_botao(painel, "Atualizar Visualização", self.gerar_arvore_grafica).pack(side="left", padx=5)
        self.criar_botao(painel, "Zoom +", self.zoom_mais).pack(side="left", padx=5)
        self.criar_botao(painel, "Zoom -", self.zoom_menos).pack(side="left", padx=5)
        self.criar_botao(painel, "Centralizar", self.centralizar_canvas).pack(side="left", padx=5)
        self.criar_botao(painel, "Limpar", self.limpar_canvas, "#2b1118").pack(side="left", padx=5)

        tk.Label(
            painel,
            text="Profundidade:",
            bg="#16070c",
            fg="#f5d6df",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(20, 5))

        tk.Spinbox(
            painel,
            from_=1,
            to=7,
            textvariable=self.limite_profundidade,
            width=5,
            bg="#240b12",
            fg="white",
            buttonbackground="#5c1020",
            font=("Segoe UI", 10)
        ).pack(side="left")

        self.label_grafico = tk.Label(
            painel,
            text="Selecione um diretório para visualizar a árvore gráfica.",
            bg="#16070c",
            fg="#e7bdc7",
            font=("Segoe UI", 10)
        )
        self.label_grafico.pack(side="left", padx=20)

        corpo = tk.Frame(self.aba_grafica, bg="#16070c")
        corpo.pack(fill="both", expand=True)

        canvas_frame = tk.Frame(corpo, bg="#240b12")
        canvas_frame.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="#100509",
            highlightthickness=0,
            scrollregion=(0, 0, 7000, 4500)
        )

        scroll_y = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        scroll_x = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        self.painel_detalhes = tk.Frame(corpo, bg="#240b12", width=280)
        self.painel_detalhes.pack(side="right", fill="y", padx=(15, 0))

        tk.Label(
            self.painel_detalhes,
            text="Detalhes do Nó",
            bg="#240b12",
            fg="white",
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", padx=18, pady=(20, 8))

        self.detalhes_texto = tk.Label(
            self.painel_detalhes,
            text="Clique em um nó da árvore.",
            bg="#240b12",
            fg="#e7bdc7",
            wraplength=240,
            justify="left",
            font=("Segoe UI", 10)
        )
        self.detalhes_texto.pack(anchor="w", padx=18, pady=10)

    def selecionar_diretorio(self):
        pasta = filedialog.askdirectory(title="Selecione uma pasta")

        if pasta:
            self.pasta_raiz = pasta
            self.popular_arvore()
            self.gerar_arvore_grafica()
            self.info.config(text=f"Diretório atual:\n{pasta}")

    def popular_arvore(self):
        self.tree.delete(*self.tree.get_children())

        nome = os.path.basename(self.pasta_raiz) or self.pasta_raiz

        raiz = self.tree.insert(
            "",
            "end",
            text=f"📁 {nome}",
            values=("Pasta", self.pasta_raiz),
            open=True
        )

        self.inserir_filhos(raiz, self.pasta_raiz)

    def inserir_filhos(self, parent, caminho):
        try:
            itens = sorted(os.listdir(caminho))
        except PermissionError:
            return
        except FileNotFoundError:
            return

        for item in itens:
            caminho_completo = os.path.join(caminho, item)

            if os.path.isdir(caminho_completo):
                node = self.tree.insert(
                    parent,
                    "end",
                    text=f"📁 {item}",
                    values=("Pasta", caminho_completo)
                )

                if self.tem_filhos(caminho_completo):
                    self.tree.insert(node, "end", text="Carregando...")
            else:
                self.tree.insert(
                    parent,
                    "end",
                    text=f"📄 {item}",
                    values=("Arquivo", caminho_completo)
                )

    def carregar_subpastas(self, event):
        item = self.tree.focus()

        if not item:
            return

        valores = self.tree.item(item, "values")

        if not valores:
            return

        caminho = valores[1]
        filhos = self.tree.get_children(item)

        if len(filhos) == 1 and self.tree.item(filhos[0], "text") == "Carregando...":
            self.tree.delete(filhos[0])
            self.inserir_filhos(item, caminho)

    def gerar_arvore_grafica(self):
        if not self.pasta_raiz:
            messagebox.showwarning("Aviso", "Selecione um diretório primeiro.")
            return

        self.limpar_canvas()
        self.desenhar_fundo_grid()

        nome_raiz = os.path.basename(self.pasta_raiz) or self.pasta_raiz

        self.label_grafico.config(text=f"Visualizando: {self.pasta_raiz}")

        dados = self.montar_dados_graficos(
            self.pasta_raiz,
            limite_profundidade=self.limite_profundidade.get()
        )

        self.desenhar_titulo_canvas(nome_raiz)

        self.desenhar_no(
            nome=nome_raiz,
            caminho=self.pasta_raiz,
            filhos=dados,
            x=3500,
            y=180,
            distancia_x=1100,
            distancia_y=210,
            nivel=0
        )

        self.centralizar_canvas()
        self.notebook.select(self.aba_grafica)

    def montar_dados_graficos(self, caminho, profundidade=0, limite_profundidade=4):
        if profundidade >= limite_profundidade:
            return []

        try:
            itens = sorted(os.listdir(caminho))[:9]
        except PermissionError:
            return [{
                "nome": "Sem permissão",
                "tipo": "bloqueado",
                "caminho": caminho,
                "filhos": []
            }]
        except:
            return []

        dados = []

        for item in itens:
            caminho_completo = os.path.join(caminho, item)

            if os.path.isdir(caminho_completo):
                dados.append({
                    "nome": item,
                    "tipo": "pasta",
                    "caminho": caminho_completo,
                    "filhos": self.montar_dados_graficos(
                        caminho_completo,
                        profundidade + 1,
                        limite_profundidade
                    )
                })
            else:
                dados.append({
                    "nome": item,
                    "tipo": "arquivo",
                    "caminho": caminho_completo,
                    "filhos": []
                })

        return dados

    def desenhar_no(self, nome, caminho, filhos, x, y, distancia_x, distancia_y, nivel):
        largura = 240
        altura = 84
        raio = 20

        tipo = "Pasta" if os.path.isdir(caminho) else "Arquivo"
        icone = "📁" if os.path.isdir(caminho) else "📄"

        if nome == "Sem permissão":
            tipo = "Bloqueado"
            icone = "🔒"
            cor_card = "#332025"
            cor_topo = "#70505a"
        elif os.path.isdir(caminho):
            cor_card = "#7a1730"
            cor_topo = "#a62645"
        else:
            cor_card = "#2b1118"
            cor_topo = "#5c1020"

        cor_borda = "#e9b8c6"
        cor_linha = "#c85d7a"

        self.canvas.create_rectangle(
            x - largura / 2 + 8,
            y - altura / 2 + 8,
            x + largura / 2 + 8,
            y + altura / 2 + 8,
            fill="#050102",
            outline=""
        )

        card = self.criar_retangulo_arredondado(
            x - largura / 2,
            y - altura / 2,
            x + largura / 2,
            y + altura / 2,
            raio,
            fill=cor_card,
            outline=cor_borda,
            width=2
        )

        self.criar_retangulo_arredondado(
            x - largura / 2,
            y - altura / 2,
            x + largura / 2,
            y - altura / 2 + 22,
            raio,
            fill=cor_topo,
            outline=cor_topo,
            width=1
        )

        nome_curto = nome if len(nome) <= 24 else nome[:24] + "..."

        texto = self.canvas.create_text(
            x,
            y - 7,
            text=f"{icone} {nome_curto}",
            fill="white",
            font=("Segoe UI", 10, "bold"),
            width=205
        )

        subtitulo = self.canvas.create_text(
            x,
            y + 25,
            text=f"{tipo} • nível {nivel} • {len(filhos)} filhos",
            fill="#f4ccd6",
            font=("Segoe UI", 8)
        )

        for elemento in (card, texto, subtitulo):
            self.canvas.tag_bind(
                elemento,
                "<Button-1>",
                lambda e, n=nome, c=caminho: self.mostrar_info_no(n, c)
            )

        quantidade = len(filhos)

        if quantidade == 0:
            return

        inicio_x = x - ((quantidade - 1) * distancia_x / 2)

        for index, filho in enumerate(filhos):
            filho_x = inicio_x + index * distancia_x
            filho_y = y + distancia_y

            self.desenhar_conexao(
                x,
                y + altura / 2,
                filho_x,
                filho_y - altura / 2,
                cor_linha
            )

            self.desenhar_no(
                nome=filho["nome"],
                caminho=filho["caminho"],
                filhos=filho["filhos"],
                x=filho_x,
                y=filho_y,
                distancia_x=max(distancia_x / 2.15, 210),
                distancia_y=distancia_y,
                nivel=nivel + 1
            )

    def criar_retangulo_arredondado(self, x1, y1, x2, y2, r=20, **kwargs):
        pontos = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]

        return self.canvas.create_polygon(
            pontos,
            smooth=True,
            splinesteps=20,
            **kwargs
        )

    def desenhar_conexao(self, x1, y1, x2, y2, cor):
        meio_y = (y1 + y2) / 2

        self.canvas.create_line(
            x1,
            y1,
            x1,
            meio_y,
            x2,
            meio_y,
            x2,
            y2,
            fill=cor,
            width=3,
            smooth=True
        )

        self.canvas.create_oval(
            x2 - 5,
            y2 - 5,
            x2 + 5,
            y2 + 5,
            fill="#ffd4df",
            outline=""
        )

    def desenhar_fundo_grid(self):
        largura = 7000
        altura = 4500
        espacamento = 80

        for x in range(0, largura, espacamento):
            self.canvas.create_line(x, 0, x, altura, fill="#1f0c12", width=1)

        for y in range(0, altura, espacamento):
            self.canvas.create_line(0, y, largura, y, fill="#1f0c12", width=1)

        for x in range(0, largura, espacamento * 4):
            self.canvas.create_line(x, 0, x, altura, fill="#32131d", width=1)

        for y in range(0, altura, espacamento * 4):
            self.canvas.create_line(0, y, largura, y, fill="#32131d", width=1)

    def desenhar_titulo_canvas(self, nome_raiz):
        self.canvas.create_text(
            3500,
            60,
            text=f"Mapa Visual da Árvore: {nome_raiz}",
            fill="white",
            font=("Segoe UI", 25, "bold")
        )

        self.canvas.create_text(
            3500,
            98,
            text="Estrutura gerada automaticamente a partir dos diretórios do computador",
            fill="#e7bdc7",
            font=("Segoe UI", 11)
        )

    def mostrar_info_no(self, nome, caminho):
        tipo = "Pasta" if os.path.isdir(caminho) else "Arquivo"

        tamanho = "-"
        if os.path.isfile(caminho):
            try:
                tamanho = f"{os.path.getsize(caminho) / 1024:.2f} KB"
            except:
                tamanho = "Não disponível"

        texto = (
            f"Nome: {nome}\n\n"
            f"Tipo: {tipo}\n\n"
            f"Tamanho: {tamanho}\n\n"
            f"Caminho:\n{caminho}"
        )

        self.detalhes_texto.config(text=texto)

    def mostrar_item_selecionado(self, event):
        item, caminho = self.obter_item_selecionado(avisar=False)

        if caminho:
            nome = os.path.basename(caminho)
            self.mostrar_info_no(nome, caminho)

    def limpar_canvas(self):
        self.canvas.delete("all")

    def zoom_mais(self):
        self.zoom_fator *= 1.1
        self.canvas.scale("all", 3500, 2200, 1.1, 1.1)

    def zoom_menos(self):
        self.zoom_fator *= 0.9
        self.canvas.scale("all", 3500, 2200, 0.9, 0.9)

    def centralizar_canvas(self):
        self.canvas.xview_moveto(0.43)
        self.canvas.yview_moveto(0.02)

    def tem_filhos(self, caminho):
        try:
            return len(os.listdir(caminho)) > 0
        except:
            return False

    def obter_item_selecionado(self, avisar=True):
        item = self.tree.focus()

        if not item:
            if avisar:
                messagebox.showwarning("Aviso", "Selecione um item da árvore.")
            return None, None

        valores = self.tree.item(item, "values")

        if not valores:
            return None, None

        return item, valores[1]

    def excluir_item(self):
        item, caminho = self.obter_item_selecionado()

        if not caminho:
            return

        confirmar = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir?\n\n{caminho}\n\nEssa ação pode ser permanente."
        )

        if not confirmar:
            return

        try:
            if os.path.isdir(caminho):
                shutil.rmtree(caminho)
            else:
                os.remove(caminho)

            self.tree.delete(item)
            self.gerar_arvore_grafica()
            messagebox.showinfo("Sucesso", "Item excluído com sucesso.")

        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao excluir:\n{erro}")

    def criar_pasta(self):
        item, caminho = self.obter_item_selecionado()

        if not caminho:
            return

        if not os.path.isdir(caminho):
            caminho = os.path.dirname(caminho)

        nome = simpledialog.askstring("Nova Pasta", "Digite o nome da nova pasta:")

        if not nome:
            return

        nova_pasta = os.path.join(caminho, nome)

        try:
            os.makedirs(nova_pasta, exist_ok=False)
            self.atualizar_arvore()
            self.gerar_arvore_grafica()
            messagebox.showinfo("Sucesso", "Pasta criada com sucesso.")

        except FileExistsError:
            messagebox.showerror("Erro", "Já existe uma pasta com esse nome.")

        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao criar pasta:\n{erro}")

    def renomear_item(self):
        item, caminho = self.obter_item_selecionado()

        if not caminho:
            return

        nome_atual = os.path.basename(caminho)

        novo_nome = simpledialog.askstring(
            "Renomear",
            "Digite o novo nome:",
            initialvalue=nome_atual
        )

        if not novo_nome:
            return

        novo_caminho = os.path.join(os.path.dirname(caminho), novo_nome)

        try:
            os.rename(caminho, novo_caminho)
            self.atualizar_arvore()
            self.gerar_arvore_grafica()
            messagebox.showinfo("Sucesso", "Item renomeado com sucesso.")

        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao renomear:\n{erro}")

    def atualizar_arvore(self):
        if not self.pasta_raiz:
            messagebox.showwarning("Aviso", "Selecione um diretório primeiro.")
            return

        self.popular_arvore()

    def abrir_explorador(self):
        item, caminho = self.obter_item_selecionado()

        if not caminho:
            return

        if os.path.isfile(caminho):
            caminho = os.path.dirname(caminho)

        try:
            if os.name == "nt":
                subprocess.Popen(f'explorer "{caminho}"')
            else:
                subprocess.Popen(["xdg-open", caminho])
        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao abrir explorador:\n{erro}")

    def expandir_tudo(self):
        for item in self.tree.get_children():
            self.expandir_item(item)

    def expandir_item(self, item):
        self.tree.item(item, open=True)

        valores = self.tree.item(item, "values")

        if valores:
            filhos = self.tree.get_children(item)

            if len(filhos) == 1 and self.tree.item(filhos[0], "text") == "Carregando...":
                self.tree.delete(filhos[0])
                self.inserir_filhos(item, valores[1])

        for filho in self.tree.get_children(item):
            self.expandir_item(filho)

    def recolher_tudo(self):
        for item in self.tree.get_children():
            self.recolher_item(item)

    def recolher_item(self, item):
        self.tree.item(item, open=False)

        for filho in self.tree.get_children(item):
            self.recolher_item(filho)


if __name__ == "__main__":
    root = tk.Tk()
    app = ArvoreDiretoriosApp(root)
    root.mainloop()