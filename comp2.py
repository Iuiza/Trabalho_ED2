import gzip

# # compactação
# # bom para textos  (algoritmo sem perda) (.txt, .json, .csv e etc)
# with open('trabalho.pdf', 'rb') as arquivo_original:
#     with gzip.open('trabalho.pdf.gz', 'wb') as arquivo_compactado:
#         arquivo_compactado.write(arquivo_original.read())

# # descompactação
# with gzip.open('trabalho.pdf.gz', 'rb') as file:
#     file_content = f.read()

# with open('arquivo_original2', 'wb') as file:
#     file.write(file_content)

# varios arquivos de uma pasta
import os

folder_path = './' # pasta que os arquivos serão compactados

for file_name in os.listdir(folder_path):
    # os.path.join(folder_path, file_name) == (folder_path + '/' + file_name)  # compara se é um arquivo
    if os.path.isfile(os.path.join(folder_path, file_name)):
        with open(os.path.join(folder_path, file_name), 'rb') as file_in:
            with gzip.open(os.path.join(folder_path, f'{file_name}.gz'), 'wb') as file_out:
                file_out.writelines(file_in)








