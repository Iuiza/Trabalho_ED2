import zipfile
import zlib

########   zipagem
# zf = zipfile.ZipFile('zipada.zip', 'w')

# zf.write('arquivo.extensao')
# zf.write('outroarquivo.extensao')
# zf.close()



#######    extração

# zf = zipfile.ZipFile('compactada.zip', 'r')
# zf.extractall()

# zf.close()



########   compressão
#compressão não é zipagem

zf = zipfile.ZipFile('compactada.zip', 'w')

# arquivo tem que estar na mesma pasta do programa
zf.write('trabalho.pdf', compress_type=zipfile.ZIP_DEFLATED)
zf.write('grafico.png', compress_type=zipfile.ZIP_DEFLATED)
zf.write('imagem.jpg', compress_type=zipfile.ZIP_DEFLATED)

zf.close()







