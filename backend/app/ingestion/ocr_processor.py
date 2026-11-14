import os
import shutil
from backend.app.core.config import settings
from backend.app.core.logging import logger

class OCRProcessor:
    def __init__(self):
        self.tesseract_available = False
        try:
            import pytesseract
            self.pytesseract = pytesseract
            
            # Check custom path or standard PATH
            if settings.TESSERACT_CMD and os.path.exists(settings.TESSERACT_CMD):
                self.pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
                self.tesseract_available = True
            elif shutil.which("tesseract"):
                self.tesseract_available = True
            else:
                # Check typical Windows paths
                typical_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe")
                ]
                for p in typical_paths:
                    if os.path.exists(p):
                        self.pytesseract.pytesseract.tesseract_cmd = p
                        self.tesseract_available = True
                        break
        except Exception as e:
            logger.warning(f"Tesseract OCR not initialized: {e}")
            self.tesseract_available = False

    def is_available(self) -> bool:
        return settings.ENABLE_OCR and self.tesseract_available

    def ocr_pixmap(self, pixmap) -> str:
        """Run OCR on a PyMuPDF pixmap."""
        if not self.is_available():
            return ""
        try:
            from PIL import Image
            import io
            img_bytes = pixmap.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            text = self.pytesseract.image_to_string(img)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed on pixmap: {e}")
            return ""

ocr_processor = OCRProcessor()

