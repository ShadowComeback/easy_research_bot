import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8501889395:AAG8Jr4rYETay7pGLCsF1E2yHX9u1IunTDc"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------- FUNCTIONS ---------- #

def get_open_access_pdf(doi: str):
    """Check Unpaywall for legal open-access PDF"""
    url = f"https://api.unpaywall.org/v2/{doi}?email=test@example.com"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("best_oa_location"):
                return data["best_oa_location"]["url_for_pdf"]
    except:
        pass
    return None


def search_arxiv(query):
    """Search arXiv if DOI not found"""
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=1"
    try:
        r = requests.get(url, timeout=10)
        if "<entry>" in r.text:
            pdf = r.text.split("<id>")[1].split("</id>")[0]
            return pdf.replace("abs", "pdf") + ".pdf"
    except:
        pass
    return None


# ---------- HANDLERS ---------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Open Access Paper Bot\n\n"
        "Send DOI or paper title.\n"
        "I will find legal free PDF if available."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()

    await update.message.reply_text("🔎 Searching...")

    pdf = None

    # If DOI
    if query.startswith("10."):
        pdf = get_open_access_pdf(query)

    # fallback search
    if not pdf:
        pdf = search_arxiv(query)

    if pdf:
        await update.message.reply_document(pdf)
    else:
        await update.message.reply_text(
            "❌ No free PDF found.\n"
            "Try another DOI or title."
        )


# ---------- MAIN ---------- #

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
