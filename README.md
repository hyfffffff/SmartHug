# Introduction

This project acts as a foundational step towards a larger-scale knowledge base initiative, with a dual focus:

1. **Model Selection**: The primary aim is to scout for the most fitting vector encoding models and expansive language models that can adeptly handle question answering. This search is pivotal for laying the groundwork of an extensive knowledge base project.
2. **Article Segmentation Testing**: A key objective is to explore and fine-tune article segmentation strategies. This ensures that the system can efficiently process and retrieve information from vast text datasets.

To facilitate these goals, the project has established a generic model interface. This interface standardizes the integration of diverse encoding and language models, making them readily testable within this framework. Initial tests have already been conducted on six popular models, including GPT, which range from online services to those deployable on local servers.

For the article segmentation aspect, the application provides users with the flexibility to experiment with various chunk lengths and overlaps. This feature is instrumental in identifying the optimal segmentation strategy, ensuring that the system can effectively manage and query large volumes of text. By enabling such customization, the project aids in refining the approach to text processing, which is crucial for the successful implementation of a knowledge base.

Moving forward, the application's design allows for the straightforward integration and testing of additional models via the predefined interface. This capability encourages users to explore a broader array of models, assessing their performance and suitability for specific tasks within the knowledge base framework. This iterative testing and evaluation process is vital for selecting the most appropriate models that can contribute to the development of a scalable and efficient knowledge base system.

# Installation

Follow these steps to set up the project environment and dependencies on your system:

### 1. Configure Python Environment

First, ensure you have Conda installed on your system. If not, download and install it from the [official Conda website](https://www.conda.io/projects/conda/en/latest/user-guide/install/index.html). Once Conda is installed, create a new Python 3.10 environment:

```bash
conda create --name smarthug python=3.10
conda activate smarthug
```

### 2. Clone the Project Repository

Clone the project repository from GitHub to your local machine. Open a terminal and run:

```bash
git clone https://github.com/hyfffffff/SmartHug/SmartHug.git
```

Make sure to replace `<your-username>` and `<project-name>` with the appropriate GitHub username and the name of the project repository.

### 3. Install PyTorch with CUDA

Install PyTorch with CUDA 11.8 support. This step is crucial for leveraging GPU acceleration (if available) for model computations. Run the following command:

```bash
conda install pytorch torchvision torchaudio cudatoolkit=11.8 -c pytorch
```

This command installs PyTorch along with torchvision and torchaudio for multimedia processing, all compatible with CUDA 11.8.

### 4. Install Project Dependencies

Navigate to your project directory and install the remaining Python dependencies using pip:

```bash
pip install -r requirements.txt
```

### 5. Install Milvus Server

The project utilizes Milvus, a highly scalable vector database, for managing and querying vectorized text data. Follow the [official Milvus installation guide](https://milvus.io/docs/v2.0.x/install_standalone-docker.md) to set up Milvus on your system. The guide provides detailed instructions for Docker-based and standalone installations.

After completing these steps, your environment should be ready for running and testing the project's functionalities.

Please ensure your system meets all hardware and software prerequisites for the above installations, especially the requirements for running Milvus and CUDA-enabled PyTorch.

# Configuration

To configure the environment for the project, you will need to set up a `.env` file that stores all the necessary environment variables, including API keys and model configurations. Follow the steps below to properly set up your environment:

### 1. Create a `.env` File

Navigate to the root directory of your project and create a new file named `.env`. This file will store all your secret keys and configurations.

### 2. Add API Keys

You will need to obtain API keys from various services to use different models and functionalities. Add the following lines to your `.env` file, replacing the placeholders with your actual API keys:

```plaintext
# API Keys
glmapi_key = 'YOUR_GLM_API_KEY'   
erniebot.api_type = "aistudio"
erniebot.access_token = "YOUR_ERNIEBOT_ACCESS_TOKEN"  
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"  
```

To obtain these keys:
- For `glmapi_key`, apply at https://open.bigmodel.cn/usercenter/apikeys.
- For `erniebot.access_token`, visit https://aistudio.baidu.com/index/accessToken.
- For `OPENAI_API_KEY`, register and obtain a key from https://openai.com/.

### 3. Network Configuration

If you're behind a proxy or need to specify no-proxy hosts, configure them as follows:

```plaintext
NO_PROXY=127.0.0.1,localhost
```

### 4. Model Configuration

Select your desired models for encoding and answering by setting their IDs in the `.env` file. Each model corresponds to a number as indicated in the comments:

```plaintext
ANSWERMODEL = 1  # Wenxin Yiyi 3.5
ENCODEMODEL = 2  # Simple Local
```

### 5. Additional Settings

Specify the name of your vector database collection and the document segmentation settings for chunk length and overlap length:

```plaintext
KBCollection = "KBCollection"
Chunk_length = 200
Overlap_length = 40
```

### 6. Save the `.env` File

After adding all the necessary configurations to the `.env` file, save and close the file. These settings will be automatically loaded by the application at runtime.

---

Make sure not to share your `.env` file or disclose its contents, as it contains sensitive API keys and configurations.

# Running the Application

After setting up your environment and configuring the `.env` file, you can run the application with its Gradio interface to interact with the models in a user-friendly way.

### Starting the Application

Launch the Gradio web interface by running the `smarthug.py` script:

```bash
python smarthug.py
```

Gradio will start a web server and provide a URL to access the interface, usually something like `http://127.0.0.1:7860/`. Open this URL in your web browser to interact with the application.

### Gradio Interface Overview

The Gradio interface is divided into two main tabs for ease of use:

1. **Document Upload and Processing**: Users can upload PDF files, which are then processed to form the knowledge base. Advanced options allow for customization of document splitting to optimize text segmentation.
![image](https://github.com/hyfffffff/SmartHug/assets/108557638/92212a4e-f005-497c-b326-9c9788000e9b)

2. **Knowledge Base Query and Answer**: This section enables users to ask questions and receive answers based on the knowledge base. The right side of the screen displays related text from the knowledge base, and users can view the original documents by clicking on "Original Document."
![picture1](https://github.com/hyfffffff/SmartHug/assets/108557638/6bd5a52a-9597-46c6-a628-c2577c13a88b)
![picture2](https://github.com/hyfffffff/SmartHug/assets/108557638/2f67fa45-49f1-459e-8b54-7872d1141abd)

### Features and Interactions

- **Flexible Model Selection**: Choose from various models for text encoding and question answering.
- **Customizable Text Segmentation**: Adjust chunk lengths and overlaps for optimal document processing.
- **Interactive Q&A**: Submit questions and receive contextually relevant answers.
- **Document Management**: Upload and view original documents for comparison and context.

### Stopping the Application

To stop the application and the Gradio web server, press `Ctrl + C` in the terminal.

