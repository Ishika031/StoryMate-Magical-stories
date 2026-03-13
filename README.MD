# Creative Storyteller: Multimodal Story Weaver

**Category:** Creative Storyteller

**Description:**  
Gemini generates interleaved text narrative + images. Google Cloud Text-to-Speech reads each scene aloud. Fluid mixed-media output (text + visuals + audio).

**Technologies:**
- Gemini model via Google GenAI SDK (text + image generation)
- Google Cloud Text-to-Speech (audio narration)
- Streamlit (UI)
- Hosted on Google Cloud Run

**Mandatory requirements met:**
- Uses Gemini interleaved/mixed output capabilities
- Hosted on Google Cloud (Cloud Run)
- At least one Google Cloud service (Text-to-Speech + Run)

**Setup locally (testing):**
1. pip install -r requirements.txt
2. Create .env with GEMINI_API_KEY=your_key
3. streamlit run app.py

**Deployment proof:** See cloud-run-proof.mp4 / .png in repo (or submission attachments)

**Demo video:** [link to your 1-2 min YouTube/Vimeo video]

**Spin-up instructions:** Included above + Dockerfile for Cloud Run