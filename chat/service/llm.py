import os
from typing import Dict, Iterator
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread

class LLMService:
    """Serviço para interagir com o modelo de linguagem"""
    
    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Carrega o modelo e tokenizer"""
        print(f"Carregando modelo {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="cpu"
        )
        print("Modelo carregado com sucesso!")
    
    def generate_response(self, prompt: str, max_tokens: int = 512) -> Dict[str, str]:
        """
        Gera uma resposta para o prompt fornecido
        
        Args:
            prompt: Pergunta/prompt do usuário
            max_tokens: Número máximo de tokens a gerar
            
        Returns:
            Dict com 'thinking' e 'response'
        """
        # Preparar mensagem com instrução clara
        system_prompt = """Você é um assistente que responde perguntas de forma clara, direta e precisa em português.

Exemplo:
Pergunta: Quem inventou a lâmpada?
Resposta: Thomas Edison inventou a lâmpada elétrica em 1879.

Agora responda a próxima pergunta de forma direta e objetiva, com no máximo 2-3 frases curtas."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Aplicar template de chat
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True
        )
        
        # Preparar inputs
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        
        # Gerar resposta
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=max_tokens
        )
        
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
        
        # Parsing do conteúdo de pensamento
        try:
            # Procura o token </think> (151668)
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0
        
        thinking = self.tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
        response = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
        
        return {
            "thinking": thinking,
            "response": response
        }
    
    def generate_response_stream(self, prompt: str, max_tokens: int = 512) -> Iterator[str]:
        """
        Gera uma resposta com streaming token por token
        
        Args:
            prompt: Pergunta/prompt do usuário
            max_tokens: Número máximo de tokens a gerar
            
        Yields:
            Eventos SSE com o texto gerado
        """
        # Preparar mensagem com instrução clara e exemplo
        system_prompt = """Você é um assistente que responde perguntas de forma clara, direta e precisa em português.

Exemplo:
Pergunta: Quem inventou a lâmpada?
Resposta: Thomas Edison inventou a lâmpada elétrica em 1879.

Agora responda a próxima pergunta de forma direta e objetiva, com no máximo 2-3 frases curtas."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Aplicar template de chat
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True
        )
        
        # Preparar inputs
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        
        # Configurar streamer
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=False
        )
        
        # Configurar geração em thread separada com parâmetros otimizados
        generation_kwargs = dict(
            **model_inputs,
            max_new_tokens=max_tokens,
            streamer=streamer,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            do_sample=True
        )
        
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        
        # Variáveis para controle
        full_text = ""
        in_thinking = False
        thinking_text = ""
        response_text = ""
        thinking_sent = False
        
        # Iterar sobre tokens gerados
        for new_text in streamer:
            # Ignorar apenas tokens vazios
            if not new_text:
                continue
            
            # Detectar e processar tags de controle ANTES de limpar
            
            # Início do pensamento
            if "<think>" in new_text:
                in_thinking = True
                new_text = new_text.replace("<think>", "")
            
            # Fim do pensamento
            if "</think>" in new_text:
                in_thinking = False
                thinking_sent = True
                parts = new_text.split("</think>", 1)
                # Enviar última parte do pensamento
                if parts[0]:
                    yield f"data: {{'type': 'thinking_chunk', 'content': {repr(parts[0])}}}\n\n"
                # Preparar resto para ser processado como resposta
                new_text = parts[1] if len(parts) > 1 else ""
                if not new_text:
                    continue
            
            # Limpar tokens especiais de fim
            new_text = new_text.replace("<|endoftext|>", "")
            new_text = new_text.replace("<|im_end|>", "")
            new_text = new_text.replace("<|end|>", "")
            
            # Enviar apenas se tiver conteúdo
            if not new_text.strip():
                continue
            
            # Enviar o chunk apropriado
            if in_thinking:
                yield f"data: {{'type': 'thinking_chunk', 'content': {repr(new_text)}}}\n\n"
            elif thinking_sent:
                yield f"data: {{'type': 'response_chunk', 'content': {repr(new_text)}}}\n\n"
        
        # Finalizar
        yield f"data: {{'type': 'done'}}\n\n"
        thread.join()


# Para execução direta (teste)
if __name__ == "__main__":
    llm = LLMService()
    result = llm.generate_response("Quem foi a primeira pessoa no espaço?")
    print("Pensamento:", result["thinking"])
    print("\nResposta:", result["response"])
