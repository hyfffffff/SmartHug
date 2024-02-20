"""
This program is designed to create a knowledge base from PDF documents using Gradio for a user-friendly interface. 

Functionality includes:
- Loading environment variables to configure models and settings such as answer model ID, encode model ID, knowledge base collection, chunk length, and overlap length.
- Initializing models for encoding and answering questions based on IDs fetched from environment variables.
- Uploading PDF files.
- Encoding uploaded PDFs into chunks, generating sentence vectors for each chunk, and adding them to a SmartBase instance to form a knowledge base.
- Allowing users to ask questions against the entire knowledge base or specific documents, selecting different models for answering, and managing document references.
- Providing a Gradio web interface to upload PDF files, configure settings, ask questions, and view answers along with references to the source documents.

The Gradio web interface includes tabs for uploading documents and asking questions, with advanced options for document processing and model selection. Users can see updates in the knowledge base in real-time, choose from pre-defined models for answering questions, and view original document snippets as image references for answers provided.
"""


import gradio as gr
import os
from pathlib import Path
from smartbase import SmartBase
from smartmodelfactory import modelfactory
import fitz
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()

answermodel_id = int(os.getenv('ANSWERMODEL'))
encodemodel_id = int(os.getenv('ENCODEMODEL'))
kbcollection = os.getenv('KBCollection')
chunk_length = int(os.getenv('Chunk_length'))
overlap_length = int(os.getenv('Overlap_length'))


answermodel = modelfactory(answermodel_id)
encodemodel = modelfactory(encodemodel_id)

pdf_folder = Path("PDFFiles")

edb = SmartBase(encodemodel=encodemodel, answermodel=answermodel, collection_name=kbcollection)

modellist = ['GPT 3.5 Turbo', '文心一言 3.5', '简单本地', '云端GLM', 'ChatGLM3-6B', 'XVERSE-13B-Chat']
appliedkbdoc = ['全部文档 All Documents']
referencelist = ["资料1", "资料2", "资料3", "资料4", "资料5"]
appliedkbdoc.extend(edb.listbasedataframe()['file_name'].tolist())




# edb.listbasedataframe()
basefiles = edb.listbasedataframe()


def upload_file(file_path):

    original_path = Path(file_path)
    file_name = original_path.name
    
    # 构建新的保存路径
    save_path = pdf_folder / file_name
    
    # 复制文件到新路径
    save_path.write_bytes(original_path.read_bytes())
    
    print(f"文件已保存到: {save_path}")



def uploadtosmartbase(list_file_obj, chunk_size, chunk_overlap):

    if list_file_obj==None:
        return edb.listbasedataframe(), None

    for file in list_file_obj:

        if Path(file).name.split('.')[1].lower() != 'pdf':
            return edb.listbasedataframe(), None

        if edb.overwrite(file, None, chunk_size, chunk_overlap):
            upload_file(file)

    return edb.listbasedataframe(), None

def anwserquestion(input_text, model, file_name, chat_history):

    nowmodel = modellist.index(edb.getanswermodel().name)

    if nowmodel!=model:
        answermodel = modelfactory(model)
        edb.setanswermodel(answermodel)

    answer, refences = edb.answer(input_text)

    chat_history.append((input_text, answer))
    answerrefence = []

    markdown_string = ""
    i = 1
    for entry in refences:
        file_name = entry[2]
        page_number = entry[1]
        text = entry[0]
        markdown_string += f"#### 资料{i} :   文件 {file_name} 页码: {page_number}\n{text}\n\n"
        answerrefence.append((file_name, page_number))
        i += 1

    return "", chat_history, markdown_string, 0, answerrefence

def updateanswermodel(selection):
    index = modellist.index(selection)
    modelid = index
    return modelid

def selectdocument(selection):
    return selection

def referencechoicechange(selection, answerreference):
    if len(answerreference)==0:
        return None
    index = referencelist.index(selection)
    (file_name, page_number) = answerreference[index]
    pdffile = "PDFFiles/" + file_name+'.pdf'

    doc = fitz.open(pdffile)
    page = doc.load_page(page_number)  # Page numbers start from 0 in PyMuPDF
    pix = page.get_pixmap()
    img_bytes = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_bytes))
    
    doc.close()
    return image


def uploadpdf():
    with gr.Blocks(theme="base") as uploadweb:
        # vector_db = gr.State()
        # qa_chain = gr.State()
        # collection_name = gr.State()

        markdown_content1 = """
            <h2>上传PDF文件，形成知识库 Upload PDF to Form Knowledge Base</h2>
            <i>上传一至多个文件。系统将判断文件是否是合格的PDF文件。对于合格的PDF文件，系统将把文件分段，形成每一段的句子向量，把段与向量插入向量数据库，开成知识库<br>
            Upload single or multiple documents. The system will validate each file as a proper PDF. Upon verification, it will chunk the PDF into sections, 
            create sentence vectors for each chunk, and insert these chunks along with their vectors into the vector database, thus building a knowledge base.</i>        
            """

        markdown_content2 = """
            <h2>向知识库提问 Ask Questions to the Knowledge Base</h2>
            <i>你可以选择适当的大模型向整个知识库或特定的文档提问<br>
            You can opt to ask questions to the entire knowledge base or to specific documents using an appropriate large-scale model.</i>
            """

        with gr.Tab("上传 Upload"):
            gr.Markdown(markdown_content1)
    
            with gr.Row():
                document = gr.Files(height=30, file_count="multiple", file_types=["PDF"], type="filepath", interactive=True, label="上传PDF文件 Upload PDF documents (single or multiple)")
                # document = PDF(label="上传PDF文件 Upload PDF documents (single or multiple)", scale=10)
                # upload_btn = gr.UploadButton("Loading document...", height=100, file_count="multiple", file_types=["pdf"], scale=1)
            with gr.Accordion("Advanced options - Document text splitter", open=False):
                with gr.Row():
                    slider_chunk_size = gr.Slider(minimum = 100, maximum = 1000, value=chunk_length, step=20, label="Chunk size", info="Chunk size", interactive=True)
                with gr.Row():
                    slider_chunk_overlap = gr.Slider(minimum = 0, maximum = 200, value=overlap_length, step=10, label="Chunk overlap", info="Chunk overlap", interactive=True)
    
            with gr.Row():
                    db_btn = gr.Button(f"上传到知识库 Upload to the Knowledge Base(Encodeing Method ：{encodemodel.name})")
            with gr.Row():
                results = gr.Dataframe(label="知识库 Knowledge Base", value=basefiles, type="pandas")
        
            
            db_btn.click(uploadtosmartbase, \
                inputs=[document, slider_chunk_size, slider_chunk_overlap], \
                outputs=[results, document])
        with gr.Tab("问答 Answer"):
                
            selectedanswermodel = gr.State(value=answermodel_id)
            selectedkbdoc = gr.State(value= '全部文档 All Documents')
            selectedreference = gr.State(value=0)
            # showreference = gr.State(value=True)
            answerreference = gr.State()

            gr.Markdown(markdown_content2)
            with gr.Row():
                with gr.Column(scale=1):
                    with gr.Row():
                        chatbot = gr.Chatbot(height=400)
                    with gr.Row():                        
                        chat_input = gr.Textbox(show_label=False, placeholder="在这里输入你的问题 Enter your question here....")
                    with gr.Row():  
                        # chat_button = gr.Button("Ask", scale = 3)
                        modelchoice = gr.Radio(label="模型 Model", choices =  modellist, show_label = False, value=modellist[selectedanswermodel.value])
                    
                    modelchoice.change(updateanswermodel, \
                                        inputs = [modelchoice], \
                                        outputs = [selectedanswermodel])
                    # with gr.Row():
                    #     conversation_log = gr.Textbox(label="对话日志", lines=10, interactive=False)
                with gr.Column(scale=1):
                    with gr.Row():
                        file_choice = gr.Dropdown(choices = appliedkbdoc, show_label = False, value=selectedkbdoc.value)
                    with gr.Row():
                        with gr.Accordion("源文档 Original Document", open=False):
                            with gr.Row():
                                referencechoice = gr.Radio(show_label=False, choices = referencelist, interactive=True)
                            with gr.Row():
                                pdfimage = gr.Image(height=1000, show_label=False)
                    with gr.Row():
                        usedkb = gr.Markdown()
                    

                file_choice.change(selectdocument, \
                                    inputs=[file_choice], \
                                    outputs=[selectedkbdoc])
                
                chat_input.submit(fn=anwserquestion, \
                                    inputs=[chat_input, selectedanswermodel, selectedkbdoc, chatbot], \
                                    outputs=[chat_input, chatbot, usedkb, selectedreference, answerreference])
                
                referencechoice.change(fn=referencechoicechange, \
                                        inputs=[referencechoice, answerreference], \
                                        outputs=[pdfimage])
                showreference = False

    

    uploadweb.launch(share=True)



if __name__ == "__main__":
    uploadpdf()