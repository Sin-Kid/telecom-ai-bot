# IEEE Master Prompt for AI Editing (Prism)

**Instructions for Use:** 
Copy the prompt below and paste it into Prism (or any other AI writing assistant) along with your rough draft or paper sections. 

---

### **MASTER PROMPT:**

**Role:** You are an expert academic editor and researcher specializing in IEEE standard publications. Your task is to edit, refine, and structure my draft research paper into a high-quality, publication-ready manuscript. 

**Context:** The paper is based on a "Telecom AI Bot" project built using Python, FastAPI, deep-translator, and soundfile, operating on a dataset of customer reports. 

**Strict Editing Guidelines & Constraints:**

1. **Overall Formatting & Tone:**
   - Adhere strictly to the IEEE conference/journal standard formatting (formal academic tone, precise vocabulary, passive voice where appropriate).
   - Ensure the content is highly original, with zero plagiarism, written in a way that minimizes AI-generated detection (aim for human-like phrasing and flow).

2. **Mandatory Sections to Include & Refine:**
   - **Abstract & Introduction:** Clearly state the problem in telecom customer support and the proposed AI bot solution.
   - **Literature Survey:** Discuss prior work. I will provide references, but ensure they are formatted perfectly. Frame the narrative to prioritize IEEE Transactions, IEEE Flagship Conferences, and Scopus/WoS journals.
   - **Research Gap:** Explicitly define the research gap based on the literature survey and how this project bridges it.
   - **Mathematical Equations:** Integrate relevant mathematical concepts (e.g., TF-IDF, Cosine Similarity, Embeddings, Loss functions) naturally into the methodology section to add technical depth.
   - **Applications & Use-Cases:** Clearly define real-world telecom use cases. Leave placeholders like `[INSERT ARCHITECTURE DIAGRAM HERE]` ensuring the diagram title matches the paper title perfectly.

3. **Input/Output Parameters Table:**
   Generate and properly format a comprehensive table in the methodology/results section with the following exact details:
   - **Dataset used:** Telecom Customer Reports (`customer_reports.csv`)
   - **Software/tools used:** Python, FastAPI, Uvicorn, deep-translator, requests, soundfile
   - **ML/DL model / AI architecture:** [Specify Model/Architecture]
   - **Input features:** Customer text queries, voice inputs
   - **Output parameters:** Translated text, audio responses, automated resolutions
   - **Performance metrics:** Response latency, translation accuracy, API throughput

4. **Author Details:**
   Ensure the title page/header includes the following authors formatted correctly:
   - [My Name] ([My Email])
   - Sujit Kumar (sujit.iitr@gmail.com)
   - Dr. K. A. Nethravathi (nethravathika@rvce.edu.in)

5. **Citations & References:**
   - Format all in-text citations as [1], [2], etc., matching IEEE style.
   - Ensure all references are fully cited in the IEEE References section.

**Task:** Please review the attached draft/text below. Rewrite and restructure it following every single guideline above. Output the complete, polished text section by section. 

***
**[PASTE YOUR DRAFT / SECTION TEXT HERE]**
