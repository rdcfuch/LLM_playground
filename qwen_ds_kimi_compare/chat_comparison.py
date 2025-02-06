import gradio as gr
import time
from kimi_selenium import KimiChatClient
from qwen_client import QwenAgent

# Initialize chat clients
kimi_client = None
qwen_client = QwenAgent()

def initialize_kimi():
    """Initialize Kimi chat client if not already initialized"""
    global kimi_client
    if kimi_client is None:
        kimi_client = KimiChatClient()
        if kimi_client.load_session():
            print("Successfully loaded Kimi session")
            kimi_client.start_chat()
        else:
            print("No previous Kimi session found, please log in manually")
            kimi_client.start_chat()
            kimi_client.store_session()

def cleanup():
    """Cleanup function to close browser when app is shutdown"""
    global kimi_client
    if kimi_client:
        kimi_client.close()

def send_question(question):
    """Send question to both chat services and return their responses"""
    if not question.strip():
        return "Please enter a question", "Please enter a question"
    
    # Initialize Kimi if needed
    if kimi_client is None:
        initialize_kimi()
    
    # Get responses from both services
    try:
        kimi_response = kimi_client.send_message(question)
        if not kimi_response:
            kimi_response = "Error: Failed to get response from Kimi"
    except Exception as e:
        kimi_response = f"Error: {str(e)}"
    
    try:
        qwen_response = qwen_client.chat(question)
        if not qwen_response:
            qwen_response = "Error: Failed to get response from Qwen"
    except Exception as e:
        qwen_response = f"Error: {str(e)}"
    
    return kimi_response, qwen_response

# Create Gradio interface
with gr.Blocks(title="AI Chat Comparison") as demo:
    gr.Markdown("# AI Chat Service Comparison")
    gr.Markdown("Compare responses from Kimi and Qwen chat services")
    
    with gr.Row():
        question_input = gr.Textbox(
            label="Your Question",
            placeholder="Type your question here...",
            lines=3
        )
    
    with gr.Row():
        submit_btn = gr.Button("Send Question")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Kimi Response")
            kimi_output = gr.Textbox(label="", lines=10)
        
        with gr.Column():
            gr.Markdown("### Qwen Response")
            qwen_output = gr.Textbox(label="", lines=10)
    
    # Connect components
    submit_btn.click(
        fn=send_question,
        inputs=[question_input],
        outputs=[kimi_output, qwen_output]
    )
    
    # Initialize Kimi client when app starts
    demo.load(fn=initialize_kimi)
    # Launch the demo
    demo.launch(share=True)

if __name__ == "__main__":
    try:
        demo.launch()
    finally:
        cleanup()