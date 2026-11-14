import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

os.makedirs("sample_papers", exist_ok=True)

def generate_attention_pdf(filename: str):
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        alignment=1, # Center
        spaceAfter=10
    )
    author_style = ParagraphStyle(
        'DocAuthor',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=1,
        spaceAfter=15
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=13.5,
        spaceAfter=8
    )

    story = []

    # PAGE 1
    story.append(Paragraph("Attention Is All You Need: Scalable Neural Sequence Transduction", title_style))
    story.append(Paragraph("Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin<br/>Google Brain, Google Research, University of Toronto", author_style))
    story.append(Paragraph("<b>Abstract</b>—The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU.", body_style))
    story.append(Paragraph("1. Introduction", heading_style))
    story.append(Paragraph("Recurrent neural networks, particularly long short-term memory (LSTM) and gated recurrent neural networks, have been firmly established as state of the art approaches in sequence modeling and transduction problems such as language modeling and machine translation. Subsequent work has continued to push the boundaries of recurrent language models and encoder-decoder architectures. Recurrent models typically factor computation along the symbol positions of the input and output sequences. Aligning the positions to steps in computation time, they generate a sequence of hidden states h_t, as a function of the previous hidden state h_{t-1} and the input for position t. This inherently sequential nature precludes parallelization within training examples, which becomes critical at longer sequence lengths, as memory constraints limit batching across examples.", body_style))
    story.append(Paragraph("2. Background", heading_style))
    story.append(Paragraph("The goal of reducing sequential computation also forms the foundation of the Extended Neural GPU, ByteNet and ConvS2S, all of which use convolutional neural networks as basic building blocks, computing hidden representations in parallel for all input and output positions. In these models, the number of operations required to relate signals from two arbitrary input or output positions grows in the distance between positions, linearly for ConvS2S and logarithmically for ByteNet. This makes it more difficult to learn dependencies between distant positions. In the Transformer this is reduced to a constant number of operations.", body_style))
    story.append(PageBreak())

    # PAGE 2
    story.append(Paragraph("3. Model Architecture", heading_style))
    story.append(Paragraph("Most competitive neural sequence transduction models have an encoder-decoder structure. Here, the encoder maps an input sequence of symbol representations (x_1, ..., x_n) to a sequence of continuous representations z = (z_1, ..., z_n). Given z, the decoder then generates an output sequence (y_1, ..., y_m) of symbols one element at a time. At each step the model is auto-regressive, consuming the previously generated symbols as additional input when generating the next.", body_style))
    story.append(Paragraph("3.1 Scaled Dot-Product Attention", heading_style))
    story.append(Paragraph("We call our particular attention 'Scaled Dot-Product Attention'. The input consists of queries and keys of dimension d_k, and values of dimension d_v. We compute the dot products of the query with all keys, divide each by sqrt(d_k), and apply a softmax function to obtain the weights on the values. In practice, we compute the attention function on a set of queries simultaneously, packed together into a matrix Q. The keys and values are also packed into matrices K and V. We compute the matrix of outputs as: Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V.", body_style))
    story.append(Paragraph("3.2 Multi-Head Attention", heading_style))
    story.append(Paragraph("Instead of performing a single attention function with d_model-dimensional keys, values and queries, we found it beneficial to linearly project the queries, keys and values h times with different, learned linear projections to d_k, d_k and d_v dimensions, respectively. On each of these projected versions of queries, keys and values we then perform the attention function in parallel, yielding d_v-dimensional output values. Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions.", body_style))
    story.append(PageBreak())

    # PAGE 3
    story.append(Paragraph("4. Training Methodology and Setup", heading_style))
    story.append(Paragraph("This section describes the training regime for our models. We trained on the standard WMT 2014 English-German dataset consisting of about 4.5 million sentence pairs. Sentences were encoded using byte-pair encoding, which has a shared source-target vocabulary of about 37000 tokens. For English-French, we used the significantly larger WMT 2014 English-French dataset consisting of 36 million sentences and split tokens into a 32000 word-piece vocabulary. Sentence pairs were batched together by approximate sequence length. Each training batch contained a set of sentence pairs containing approximately 25000 source tokens and 25000 target tokens.", body_style))
    story.append(Paragraph("4.1 Hardware and Schedule", heading_style))
    story.append(Paragraph("We trained our models on one machine with 8 NVIDIA P100 GPUs. For our base models using the hyperparameters described throughout the paper, each training step took about 0.4 seconds. We trained the base models for a total of 100,000 steps or 12 hours. For our big models, step time was 1.0 seconds. The big models were trained for 300,000 steps (3.5 days). We used the Adam optimizer with beta_1 = 0.9, beta_2 = 0.98 and epsilon = 10^-9.", body_style))
    story.append(PageBreak())

    # PAGE 4
    story.append(Paragraph("5. Experimental Results", heading_style))
    story.append(Paragraph("On the WMT 2014 English-to-German translation task, the big transformer model (Transformer (big)) outperforms the best previously reported models (including ensembles) by more than 2.0 BLEU, establishing a new state-of-the-art BLEU score of 28.4. The configuration of this model is listed in Table 1 below. Training took 3.5 days on 8 P100 GPUs. Even our base model surpasses all previously published models and ensembles, at a fraction of the training cost.", body_style))
    
    table_data = [
        ['Model', 'BLEU (EN-DE)', 'BLEU (EN-FR)', 'Training FLOPs (10^18)'],
        ['ByteNet', '23.75', '-', '1.0'],
        ['ConvS2S', '25.16', '40.46', '9.6'],
        ['MoE (Shazeer 2017)', '26.03', '40.56', '20.0'],
        ['Transformer (base)', '27.3', '38.1', '3.3'],
        ['Transformer (big)', '28.4', '41.8', '23.0']
    ]
    t = Table(table_data, colWidths=[150, 100, 100, 130])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#026fc7')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    story.append(t)
    story.append(Spacer(1, 15))
    story.append(Paragraph("6. Limitations and Future Work", heading_style))
    story.append(Paragraph("Despite dramatic performance improvements, the self-attention mechanism exhibits quadratic memory complexity with respect to sequence length O(N^2), making document-level context generation challenging. Future work involves extending the Transformer to modalities other than text, including images, audio, and video, and investigating efficient restricted attention mechanisms for sequences with tens of thousands of tokens.", body_style))

    doc.build(story)
    print(f"Generated {filename}")

def generate_bert_pdf(filename: str):
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        alignment=1,
        spaceAfter=10
    )
    author_style = ParagraphStyle(
        'DocAuthor',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=1,
        spaceAfter=15
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=13.5,
        spaceAfter=8
    )

    story = []

    # PAGE 1
    story.append(Paragraph("BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", title_style))
    story.append(Paragraph("Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova<br/>Google AI Language", author_style))
    story.append(Paragraph("<b>Abstract</b>—We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers. As a result, the pre-trained BERT model can be fine-tuned with just one additional output layer to create state-of-the-art models for a wide range of tasks, such as question answering and language inference, without substantial task-specific architecture modifications. BERT is conceptually simple and empirically powerful. It obtains new state-of-the-art results on eleven natural language processing tasks, including pushing the GLUE score to 80.5% (7.7% point absolute improvement), MultiNLI accuracy to 86.7% (4.6% absolute improvement) and SQuAD v1.1 question answering Test F1 to 93.2 (1.5 point absolute improvement).", body_style))
    story.append(Paragraph("1. Introduction", heading_style))
    story.append(Paragraph("Language model pre-training has been shown to be effective for improving many natural language processing tasks. There are two existing strategies for applying pre-trained language representations to downstream tasks: feature-based and fine-tuning. The feature-based approach, such as ELMo, uses task-specific architectures that include the pre-trained representations as additional features. The fine-tuning approach, such as the Generative Pre-trained Transformer (OpenAI GPT), introduces minimal task-specific parameters, and is trained on the downstream tasks by simply fine-tuning all pretrained parameters. In this paper, we argue that current techniques restrict the power of pre-trained representations, especially for fine-tuning approaches. The major limitation is that standard language models are unidirectional, and this limits the choice of architectures that can be used during pre-training.", body_style))
    story.append(PageBreak())

    # PAGE 2
    story.append(Paragraph("2. BERT Architecture and Methodology", heading_style))
    story.append(Paragraph("There are two steps in our framework: pre-training and fine-tuning. During pre-training, the model is trained on unlabeled data over different pre-training tasks. For fine-tuning, the BERT model is first initialized with the pre-trained parameters, and all of the parameters are fine-tuned using labeled data from downstream tasks. BERT's model architecture is a multi-layer bidirectional Transformer encoder based on the original implementation described in Vaswani et al. (2017). We denote the number of layers as L, the hidden size as H, and the number of self-attention heads as A. We report results on two model sizes: BERT_BASE (L=12, H=768, A=12, Total Parameters=110M) and BERT_LARGE (L=24, H=1024, A=16, Total Parameters=340M).", body_style))
    story.append(Paragraph("2.1 Pre-training Tasks", heading_style))
    story.append(Paragraph("Task 1: Masked LM (MLM). Standard conditional language models can only be trained left-to-right or right-to-left, since bidirectional conditioning would allow each word to indirectly 'see itself' in a multi-layered context. In order to train a deep bidirectional representation, we simply mask a random 15% of the input tokens at random, and then predict those masked tokens. Task 2: Next Sentence Prediction (NSP). In order to train a model that understands sentence relationships, we pre-train for a binarized next sentence prediction task that can be trivially generated from any monolingual corpus. When choosing sentences A and B for each pretraining example, 50% of the time B is the actual next sentence that follows A, and 50% of the time it is a random sentence from the corpus.", body_style))
    story.append(PageBreak())

    # PAGE 3
    story.append(Paragraph("3. Datasets and Experimental Results", heading_style))
    story.append(Paragraph("For the pre-training corpus, we use the BooksCorpus (800M words) and English Wikipedia (2,500M words). For Wikipedia, we extract only text passages and ignore lists, tables, and headers. We evaluate BERT on the General Language Understanding Evaluation (GLUE) benchmark, which consists of nine sentence or sentence-pair tasks.", body_style))
    
    bert_table_data = [
        ['System', 'MNLI (acc)', 'QNLI (acc)', 'QQP (F1)', 'SST-2 (acc)', 'GLUE Score'],
        ['Pre-OpenAI SOTA', '80.6', '82.3', '66.1', '90.4', '74.0'],
        ['OpenAI GPT', '82.1', '87.4', '70.3', '91.3', '75.1'],
        ['BERT_BASE', '84.6', '90.5', '71.2', '93.5', '79.6'],
        ['BERT_LARGE', '86.7', '92.7', '72.1', '94.9', '80.5']
    ]
    bt = Table(bert_table_data, colWidths=[120, 80, 80, 80, 80, 80])
    bt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#074b85')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    story.append(bt)
    story.append(Spacer(1, 15))
    story.append(Paragraph("4. Limitations and Future Work", heading_style))
    story.append(Paragraph("A primary limitation of BERT is the discrepancy between pre-training and fine-tuning, because the [MASK] token never appears during fine-tuning. Furthermore, pre-training is computationally prohibitive, requiring 64 Cloud TPU chips for 4 days for BERT_LARGE. Future research directions include developing sample-efficient pre-training methods and extending bidirectional contextual training to cross-lingual and multimodal representation learning.", body_style))

    doc.build(story)
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_attention_pdf("sample_papers/attention_paper.pdf")
    generate_bert_pdf("sample_papers/bert_paper.pdf")

