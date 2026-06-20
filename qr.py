from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import unicodedata
import re


# THÔNG TIN TÀI KHOẢN MB BANK

BANK_ID = "970422"
ACCOUNT_NO = "0326150214"
ACCOUNT_NAME = "TRUONG VAN AN"


def remove_vietnamese_accents(text):
    if text is None:
        return ""

    text = str(text)
    text = unicodedata.normalize("NFD", text)
    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )

    text = text.replace("Đ", "D").replace("đ", "d")
    return text


def clean_transfer_text(text, max_length=50):

    text = remove_vietnamese_accents(text)
    text = re.sub(r"[^A-Za-z0-9 ]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_length]


def create_payment_qr(customer_name, pet_name, service_name, amount, bill_code):


    current_dir = Path(__file__).resolve().parent

    if current_dir.name == "pages":
        project_root = current_dir.parent
    else:
        project_root = current_dir

    qr_folder = project_root / "assets" / "qr_codes"
    qr_folder.mkdir(parents=True, exist_ok=True)

    # Xử lý số tiền
    amount_text = str(amount).replace(",", "").replace("đ", "").replace(" ", "")
    amount_int = int(float(amount_text))

    if amount_int <= 0:
        raise ValueError("Số tiền thanh toán phải lớn hơn 0.")

    # Làm sạch thông tin
    account_no = str(ACCOUNT_NO).strip().replace(" ", "")
    account_name = clean_transfer_text(ACCOUNT_NAME, max_length=50)

    transfer_content = clean_transfer_text(
        f"{bill_code} {customer_name} {pet_name}",
        max_length=50
    )

    params = urlencode({
        "amount": amount_int,
        "addInfo": transfer_content,
        "accountName": account_name
    })

    # Dùng .jpg để ổn định hơn khi tải ảnh
    qr_url = (
        f"https://img.vietqr.io/image/"
        f"{BANK_ID}-{account_no}-compact2.jpg"
        f"?{params}"
    )

    qr_path = qr_folder / f"{bill_code}.jpg"

    # Lưu lại link để nếu lỗi có thể mở thử trên trình duyệt
    debug_url_path = qr_folder / f"{bill_code}_url.txt"
    debug_url_path.write_text(qr_url, encoding="utf-8")

    try:
        request = Request(
            qr_url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urlopen(request, timeout=20) as response:
            image_data = response.read()

        with open(qr_path, "wb") as file:
            file.write(image_data)

        return str(qr_path)

    except HTTPError as e:
        if e.code == 525:
            raise Exception(
                "VietQR đang trả về lỗi 525. "
                "Hãy kiểm tra lại BANK_ID, số tài khoản, tên tài khoản, "
                "hoặc mở file *_url.txt trong thư mục assets/qr_codes để test link trên trình duyệt."
            )
        else:
            raise Exception(f"Lỗi HTTP khi tạo QR: {e.code}")

    except URLError as e:
        raise Exception(
            f"Không thể kết nối tới VietQR. Kiểm tra lại mạng Internet.\n{str(e)}"
        )