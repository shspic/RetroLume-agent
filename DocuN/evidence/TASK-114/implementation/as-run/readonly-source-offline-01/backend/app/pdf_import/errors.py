"""PDF 解析组件对调用方暴露的稳定错误。"""


class PdfImportError(Exception):
    """所有可预期 PDF 导入失败的基类。"""

    code = "pdf_import_failed"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class PdfInputTooLargeError(PdfImportError):
    code = "pdf_input_too_large"


class PdfInvalidError(PdfImportError):
    code = "pdf_invalid"


class PdfEncryptedError(PdfImportError):
    code = "pdf_encrypted"


class PdfNoExtractableTextError(PdfImportError):
    code = "pdf_no_extractable_text"


class PdfPageLimitError(PdfImportError):
    code = "pdf_page_limit_exceeded"


class PdfTextLimitError(PdfImportError):
    code = "pdf_text_limit_exceeded"


class PdfTimeoutError(PdfImportError):
    code = "pdf_timeout"


class PdfUnsupportedPlatformError(PdfImportError):
    code = "pdf_unsupported_platform"


class PdfSandboxSetupError(PdfImportError):
    code = "pdf_sandbox_setup_failed"


class PdfProtocolError(PdfImportError):
    code = "pdf_worker_protocol_invalid"


class PdfWorkerError(PdfImportError):
    code = "pdf_worker_failed"
