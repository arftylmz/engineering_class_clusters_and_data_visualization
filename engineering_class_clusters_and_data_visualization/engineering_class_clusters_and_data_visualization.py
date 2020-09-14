from tkinter import *
import urllib.request as urllib2
import ssl
from bs4 import BeautifulSoup
import re
import clusters
import time
class Editor(Frame):

    def __init__(self,parent):
        Frame.__init__(self, parent)
        self.root=parent
        self.initUI()

    def initUI(self):
        self.listbox_list = []
        self.sozluk = {}
        self.yeniSozluk = {}
        self.liste = []
        self.grid()
        frame = Frame(self, bg="Beige", width="850", height="700", pady="25", padx="10")
        frame.grid()

        #veri seti yüklenen kısım
        self.Baslik = Label(frame, text="veri seti yükleyin", fg="Blue", bg="Beige")
        self.Baslik.config(font=("Courier", 14, "bold italic"))
        self.Baslik.grid(row=0, column=1)
        self.button = Button(frame, text="Veri Seti Yükle", fg="Blue", bg="Gold",command = self.veriYukle)
        self.button.grid(row=0, column=0)

        self.benzerlik_label = Label(frame, text="Benzerlik ölçütü", fg="Blue", bg="Beige")
        self.benzerlik_label.config(font=("Courier", 14, "bold italic"))
        self.benzerlik_label.grid(row=5, column=0, columnspan=1)
        self.method = Label(frame, text="Ders kodu örnekleri", fg="Blue", bg="Beige")
        self.method.config(font=("Courier", 14, "bold italic"))
        self.method.grid(row=5, column=3,sticky = W)

        #######Listbox ve Scrollbar ######
        self.scroll = Scrollbar(frame, orient=VERTICAL, width=35)
        self.listbox = Listbox(frame, width=30, selectmode=MULTIPLE, fg="Blue", bg="Beige", yscrollcommand=self.scroll)
        self.listbox.bind("<<ListboxSelect>>", self.onSelect)
        self.listbox.grid(row=5, column=5, sticky=E)
        self.scroll.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scroll.set)
        self.scroll.grid(row=5, column=6, sticky=N + S + W)


        ###Radio Button#####
        self.kumeleme = IntVar()
        self.radio1 = Radiobutton(frame, text="Pearson", value=0, variable=self.kumeleme, fg="Blue", bg="Beige")
        self.radio2 = Radiobutton(frame, text="Tanimoto", value=1, variable=self.kumeleme, fg="Blue", bg="Beige")
        self.radio1.grid(row=5, column=1, sticky=N + S + E + W, padx="30")
        self.radio2.grid(row=5, column=1, sticky=S, padx="30")

        ###Canvas ve Scrollbar oluşturmak###
        self.canvas=Canvas(frame,bg='#FFFFFF',scrollregion=(0,0,25000,25000))
        self.canvas.grid(row=8, column=0, columnspan=6, sticky=W + E)
        self.hbar = Scrollbar(frame, orient=HORIZONTAL)
        self.hbar.grid(row=9, column=0, columnspan=6, sticky=W + E + N)
        self.hbar.config(command=self.canvas.xview)
        self.vbar = Scrollbar(frame, orient=VERTICAL)
        self.vbar.grid(row=8, column=6, sticky=N + S + W)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)


        self.buttonkume = Button(frame, text="Hiyerarşik kümeleri göster", fg="Blue", bg="Gold",command = self.kumele)
        self.buttonkume.grid(row=7, column=0,sticky = E)
        self.buttonmatris = Button(frame, text="Veri Matrisini göster", fg="Blue", bg="Gold",command = self.matrisGoster)
        self.buttonmatris.grid(row=7, column=3,sticky = E)
        self.boslabel = Label(frame, text="")
        self.boslabel.grid(row=6, column=0, columnspan=6)

    def getheight(self,clust):
        # Is this an endpoint? Then the height is just 1
        if clust.left == None and clust.right == None: return 1

        # Otherwise the height is the same of the heights of
        # each branch
        return self.getheight(clust.left) + self.getheight(clust.right)

    def getdepth(self,clust):
        # The distance of an endpoint is 0.0
        if clust.left == None and clust.right == None: return 0

        # The distance of a branch is the greater of its two sides
        # plus its own distance
        return max(self.getdepth(clust.left), self.getdepth(clust.right)) + clust.distance

    def drawdendrogram(self,clust, labels):
        # height and width
        h = self.getheight(clust) * 10
        w = 1200
        depth = self.getdepth(clust)
        scaling = float(w - 150) / depth


        self.canvas.create_line(w/2, 0, w/2, 10)
        # Draw the first node
        self.drawnode( clust, w/2, 10, scaling, labels)


    def drawnode(self, clust, x, y, scaling, labels):
        if clust.id < 0:
            h1 = self.getheight(clust.left) *10
            h2 = self.getheight(clust.right) *10
            top = x - (h1 + h2) / 2
            bottom = x + (h1 + h2) / 2
            print(h1, h2, top, bottom)

            # Line length
            ll = (clust.distance * scaling)
            # Vertical line from this cluster to children
            self.canvas.create_line((top + h1 / 2) - ll/4 , y, bottom - h2 / 2 + ll/4, y)

            # Horizontal line to left item
            self.canvas.create_line((top + h1 / 2) - ll/4, y, top + h1 / 2 - ll/4, y + h1)

            # Horizontal line to right item
            self.canvas.create_line(bottom - h2 / 2 + ll/4, y, bottom - h2 / 2 + ll/4,y + h2)

            # Call the function to draw the left and right nodes
            self.drawnode(clust.left, top + h1 / 2 - ll/4, y + h1, scaling, labels)
            self.drawnode(clust.right, bottom - h2 / 2 + ll/4 , y + h2, scaling, labels)

        else:
            # If this is an endpoint, draw the item label
            for i in labels[clust.id]:
                print(i)
                self.canvas.create_text(x, y + 5, text=str(i))
                y = y + 10

            # DİLENDİĞİ TAKTİRDE YAZILAR NORMAL ŞEKLİNDE YAZDIRILABİLİR
            # ANLAM BÜTÜNLÜĞÜ KORUNMASI AÇISINDAN YAZILAR YATAY BİR FORMATTA YAZILMIŞTIR.
            # self.canvas.create_text(x , y + 5 ,text = labels[clust.id])





    # Hiyerarşik kümeleme yan çizilmek istenildiği takdirde bu fonksiyon kullanılabilir.
    # def getheight(self,clust):
    #
    #     if clust.left == None and clust.right == None: return 1
    #     return self.getheight(clust.left) + self.getheight(clust.right)
    #
    # def getdepth(self,clust):
    #
    #     if clust.left == None and clust.right == None: return 0
    #     return max(self.getdepth(clust.left), self.getdepth(clust.right)) + clust.distance
    #
    # def drawdendrogram(self,clust, labels, jpeg='clusters.jpg'):
    #
    #     h = self.getheight(clust) * 20
    #     w = 1200
    #     depth = self.getdepth(clust)
    #
    #
    #     scaling = float(w - 150) / depth
    #     self.canvas.create_line(0, h / 2, 10, h / 2)
    #     self.drawnode( clust, 10, (h / 2), scaling, labels)
    #
    # def drawnode(self, clust, x, y, scaling, labels):
    #     if clust.id < 0:
    #         h1 = self.getheight(clust.left) * 20
    #         h2 = self.getheight(clust.right) * 20
    #         top = y - (h1 + h2) / 2
    #         bottom = y + (h1 + h2) / 2
    #         print(h1, h2, top, bottom)
    #
    #
    #         ll = clust.distance * scaling
    #         # Vertical line from this cluster to children
    #         #draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(255, 0, 0))
    #
    #         self.canvas.create_line(x, top + h1 / 2, x, bottom - h2 / 2)
    #         # Horizontal line to left item
    #         self.canvas.create_line(x, top + h1 / 2, x + ll, top + h1 / 2)
    #         #draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill=(255, 0, 0))
    #
    #         # Horizontal line to right item
    #         self.canvas.create_line(x, bottom - h2 / 2, x + ll, bottom - h2 / 2)
    #         #draw.line((x, bottom - h2 / 2, x + ll, bottom - h2 / 2), fill=(255, 0, 0))
    #
    #         # Call the function to draw the left and right nodes
    #         self.drawnode( clust.left, x + ll, top + h1 / 2, scaling, labels)
    #         self.drawnode( clust.right, x + ll, bottom - h2 / 2, scaling, labels)
    #     else:
    #         # If this is an endpoint, draw the item label
    #         self.canvas.create_text(x + 5, y - 7 ,text = labels[clust.id])


    def arama(self,sozluk, listbox_list):
        self.yeniSozluk.clear()
        for i in listbox_list:
            for key in sozluk:
                reg = re.search(i, key)
                if reg:
                    self.yeniSozluk.setdefault(key, {})
                    for items in sozluk[key]:
                        self.yeniSozluk[key][items] = self.sozluk[key][items]
        return self.yeniSozluk

    def matrisOlustur(self,sozluk):

        out_file = open("matris.txt", "w", encoding="UTF-8")
        out_file.write("Dersler")
        columnslist = []


        for value in sozluk.values():
            for key in value:
                if key not in columnslist:
                    columnslist.append(key)


        for column in columnslist:
            out_file.write('\t%s' % column)
        out_file.write('\n')

        for key, value in sozluk.items():
            out_file.write(key)
            out_file.write('\t')

            for column in columnslist:
                if column not in value:
                    out_file.write('0\t')
                else:
                    out_file.write(str(value[column]))
                    out_file.write('\t')
            out_file.write('\n')
        out_file.close()
        self.file = out_file


    def animate(self, i,name):
        # Animasyonu yapıyoruz ( . . . . . )
        self.Baslik.config(text=f"( {'..' * i} ) \n"+name+" yükleniyor")
        self.update_idletasks()

    def onSelect(self,val):
        try:
            self.liste.clear()
            idx = self.listbox.curselection()
            for i in idx:
                self.value = self.listbox.get(i)
                if self.value not in self.liste:
                    self.liste.append(self.value)




        except:
            print("")


    def veriYukle(self):
        self.canvas.delete("all")
        gcontext = ssl.SSLContext()
        name="Veri Seti"
        a=1
        for i in range(1, 7):
            #here is the animation
            if a < 7:
                # Animasyonu çağırıyoruz ( . . . . . )
                self.animate(a,name)
                a += 1
                time.sleep(0.1)
        for i in range(1, 7):

            c = urllib2.urlopen(
                "https://www.istinye.edu.tr/apps/ders-icerikleri.php?program_kodu=040" + str(i) + "001&dil=tr",
                context=gcontext)
            contents = c.read()
            soup = BeautifulSoup(contents, features="html.parser")
            for i in soup.find_all(class_=re.compile("derscontainer")):
                cemal = i.get_text()
                x = cemal.split("\n")
                if x[8] == '':
                    continue
                cemal = re.search("[A-Z]+", x[3])
                self.sozluk.setdefault(x[3], {})
                split = x[8].split(" ")
                for j in split:
                    if len(j) > 2:
                        regex = re.compile(r'[,.:;?!()]|[\r]').sub('', j)
                        son = str(regex).lower()
                        if son in self.sozluk[x[3]]:
                            self.sozluk[x[3]][son] += 1
                        else:
                            self.sozluk[x[3]][son] = 1
                if cemal.group() in self.listbox_list:
                    continue
                else:
                    self.listbox_list.append(cemal.group())
        self.listbox_list.sort()
        for i in self.listbox_list:
            self.listbox.insert(END,i)
        self.Baslik.config(text="veri seti yüklendi.")

    def matrisGoster(self):

        self.canvas.delete("all")
        if len(self.liste) == 0 :
            self.matrisOlustur(self.sozluk)

        else:
            self.yeniSozluk = self.arama(self.sozluk, self.liste)
            self.matrisOlustur(self.yeniSozluk)

        if self.file:
            count2 = 0
            count = 0
            self.file = open("matris.txt", "r+", encoding='UTF-8').readlines()
            for i in self.file:
                count += 1

            deneme = open("matris.txt", "r+", encoding='UTF-8').readline()

            for i in deneme:
                count2 +=1

            self.file = open("matris.txt", "r+", encoding='UTF-8').read()
            a = 8
            self.canvas.create_text((count2)*(15/4), a*count + 10, text=self.file)
            self.canvas.update()




    def kumele(self):
        self.canvas.delete("all")
        name="Kümeleme"
        i=1
        self.animate(i,name)
        i+=1
        #FİLTRELEME
        #print(self.listbox_list)
        if len(self.liste) == 0 :
            self.matrisOlustur(self.sozluk)
            self.animate(i,name)
            i+=1
        else:
            self.yeniSozluk = self.arama(self.sozluk, self.liste)
            self.animate(i,name)
            i+=1
            self.matrisOlustur(self.yeniSozluk)

        karar = self.kumeleme.get()
        self.animate(i,name)
        i+=1
        if karar == 0:
            blognames, words, data = clusters.readfile('matris.txt')
            clust = clusters.hcluster(data, distance=clusters.pearson)
            self.drawdendrogram(clust, blognames)
            self.animate(i,name)
        elif karar == 1:
            blognames, words, data = clusters.readfile('matris.txt')
            clust = clusters.hcluster(data, distance=clusters.tanamoto)
            self.drawdendrogram(clust, blognames)
            self.animate(i,name)
        self.Baslik.config(text="kümeleme yüklendi.")






def main():
    root= Tk()
    root.title("Excel-Reader")
    root.geometry("830x570+300+100")
    #konumu ayarlıyoruz ve ekran boyut ayarlamasını kapatıyoruz.
    root.resizable(FALSE,FALSE)
    App = Editor(root)
    root.mainloop()



if __name__ == '__main__':
    main()
