EasyRAG: Easy Retrieval Augmented Generation 🚀
===============================================

Overview
--------

EasyRAG turns your local machine into a powerful AI assistant. By indexing your documents, it enhances language models like llama2 or command R, reducing hallucinations and providing potentially more accurate, context-aware responses. Designed for simplicity, it ensures your data stays private and local. 🛡️

![](https://github.com/2ToTheNthPower/easy-rag/blob/main/resources/demo.gif)

Features
--------

*   **Local Data Indexing:** Helps keep your LLM grounded and relevant.
*   **100% Private:** Your data never leaves your machine. 🚫🌐🚫
*   **Easy Setup:** Straightforward for users on Linux w/ Nvidia GPUs. 🐧
*   **Fully Offline (After Setup):** Works without an internet connection after downloading models. 🚫📶🚫

Get Started
-----------

Prerequisites
-------------

Note that linux is the only supported operating system at the moment.  Porting this to other operating systems is very doable, but requires me to mess around with virtual machine networks and potentially running Ollama outside of my set of containers so accelerated inference will be easier to setup.  If you are interested in porting this to another operating system, please make a pull request with your proposed changes.

Before getting started, make sure you have the following prerequisites installed:

*   **Podman:** Podman is a daemonless container engine for developing, managing, and running OCI Containers. You can install Podman by following the instructions for your specific operating system. Visit the [Podman website](https://podman.io/getting-started/installation) for installation instructions.

*   **Setup Nvidia GPU for accelerated inference:** CDI (Container Device Interface) is a specification that helps containers access your system's hardware. To set up CDI for Nvidia GPU, follow the instructions found [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/cdi-support.html).

Installation Steps
------------------

Follow these steps to get started with EasyRAG:

1.  **Clone:** `git clone https://github.com/2ToTheNthPower/easy-rag.git`
2.  **Navigate:** `cd easy-rag`
3.  **Add your data:** Add your data to the `data` directory. You can add text files, PDFs, or any other document type you want to index.  Most common text file types are supported by default.
4.  **(Optional) Setup GPU:** Follow the instructions to set up CDI for Nvidia GPU.  If you choose not to run with a GPU, you can remove the `--device` flag from the `docker-compose.yml
5.  **Run:** `podman compose up`
6.  **Visit:** `http://localhost:8501` to download models, index data, and start chatting!
7.  **Download models:** Click on the "Pull new models" button to download the models you want to use.  This only needs to be done once per model.  The models are stored in the `ollama` directory.  The recommended starting chat model is `command-r:35b-v0.1-q2_K` and the recommended starting embedding model is `nomic-embed-text:latest`.  Both of these models can run on an RTX 3090 with 24GB of VRAM, and command-R is currently one of the best open source chat models for RAG.  If you have a smaller GPU, you may want to try the `llama2` model instead.
8.  **Index your data:** Click on the "Create data embeddings" button to index the data you placed in the data folder.  This reindexes all the data in the folder every time you click the button, so if you add new data, you will need to click the button again.  Depending on the amount of data and the model you have selected for creating embeddings, this can take a while.
9.  **Chat:** Start chatting with your AI assistant! 🚀

