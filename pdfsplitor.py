import fitz  # PyMuPDF

class PDFSplitor:
    def __init__(self, file_name):
        self.file_name = file_name
        self.text = ""
        self.pages = []
        self.valid = False  # Attribute indicating if the PDF was successfully processed
        self.extract_text_from_pdf()

    def extract_text_from_pdf(self):
        """Extract text from the given PDF file."""
        try:
            doc = fitz.open(self.file_name)
            for page_num, page in enumerate(doc):
                self.pages.append([page_num, len(self.text)])
                text = page.get_text()
                self.text += text
            doc.close()
            self.valid = True  # PDF was successfully processed
        except Exception as e:
            print(f"Error opening PDF file {self.file_name}: {e}")
            self.valid = False

        if len(self.text) == 0:
            self.valid = False

    # def get_chunk(self, length, overlap=0):
    #     """Split the text into segments of a given length, noting the page number."""
    #     if not self.valid:
    #         return None  # Early return if the PDF was not successfully processed

    #     segments = []
    #     page_num = 0

    #     for i in range(0, len(self.text), length):
    #         # Find the first page number that corresponds to the start of the segment
    #         while page_num < len(self.pages) - 1 and i >= self.pages[page_num + 1][1]:
    #             page_num += 1
    #         segment = self.text[i:i + length]
    #         segments.append((self.pages[page_num][0], segment))
    #     return segments
    
    def get_chunk(self, length, overlap=0):
        """Split the text into segments of a given length, noting the page number, considering an overlap."""
        if not self.valid:
            return None  # Early return if the PDF was not successfully processed

        segments = []
        page_num = 0
        start_index = 0
        end_index = 0

        while start_index < len(self.text) - overlap:
            # Adjust the end index of the segment considering the overlap
            end_index = min(start_index + length, len(self.text))
            segment = self.text[start_index:end_index]

            # Find the page number for the current segment
            while page_num < len(self.pages) - 1 and start_index >= self.pages[page_num + 1][1]:
                page_num += 1

            # Add the segment and corresponding page number to the list
            segments.append((self.pages[page_num][0], segment))

            # Update the start index for the next segment
            start_index = end_index - overlap

            # Ensure the next segment does not start with negative index
            start_index = max(start_index, 0)


        return segments


