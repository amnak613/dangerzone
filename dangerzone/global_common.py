import gzip
import json
import logging
import pathlib
import platform
import shutil
import subprocess
import sys
from typing import Optional

import appdirs
import colorama

from .container import convert
from .settings import Settings
from .util import get_resource_path

log = logging.getLogger(__name__)


class GlobalCommon(object):
    """
    The GlobalCommon class is a singleton of shared functionality throughout the app
    """

    def __init__(self) -> None:
        # Initialize terminal colors
        colorama.init(autoreset=True)

        # App data folder
        self.appdata_path = appdirs.user_config_dir("dangerzone")

        # Container
        self.container_name = "dangerzone.rocks/dangerzone"

        # Languages supported by tesseract
        self.ocr_languages = {
            "Afrikaans": "ar",
            "Albanian": "sqi",
            "Amharic": "amh",
            "Arabic": "ara",
            "Arabic script": "Arabic",
            "Armenian": "hye",
            "Armenian script": "Armenian",
            "Assamese": "asm",
            "Azerbaijani": "aze",
            "Azerbaijani (Cyrillic)": "aze_cyrl",
            "Basque": "eus",
            "Belarusian": "bel",
            "Bengali": "ben",
            "Bengali script": "Bengali",
            "Bosnian": "bos",
            "Breton": "bre",
            "Bulgarian": "bul",
            "Burmese": "mya",
            "Canadian Aboriginal script": "Canadian_Aboriginal",
            "Catalan": "cat",
            "Cebuano": "ceb",
            "Cherokee": "chr",
            "Cherokee script": "Cherokee",
            "Chinese - Simplified": "chi_sim",
            "Chinese - Simplified (vertical)": "chi_sim_vert",
            "Chinese - Traditional": "chi_tra",
            "Chinese - Traditional (vertical)": "chi_tra_vert",
            "Corsican": "cos",
            "Croatian": "hrv",
            "Cyrillic script": "Cyrillic",
            "Czech": "ces",
            "Danish": "dan",
            "Devanagari script": "Devanagari",
            "Divehi": "div",
            "Dutch": "nld",
            "Dzongkha": "dzo",
            "English": "eng",
            "English, Middle (1100-1500)": "enm",
            "Esperanto": "epo",
            "Estonian": "est",
            "Ethiopic script": "Ethiopic",
            "Faroese": "fao",
            "Filipino": "fil",
            "Finnish": "fin",
            "Fraktur script": "Fraktur",
            "Frankish": "frk",
            "French": "fra",
            "French, Middle (ca.1400-1600)": "frm",
            "Frisian (Western)": "fry",
            "Gaelic (Scots)": "gla",
            "Galician": "glg",
            "Georgian": "kat",
            "Georgian script": "Georgian",
            "German": "deu",
            "Greek": "ell",
            "Greek script": "Greek",
            "Gujarati": "guj",
            "Gujarati script": "Gujarati",
            "Gurmukhi script": "Gurmukhi",
            "Hangul script": "Hangul",
            "Hangul (vertical) script": "Hangul_vert",
            "Han - Simplified script": "HanS",
            "Han - Simplified (vertical) script": "HanS_vert",
            "Han - Traditional script": "HanT",
            "Han - Traditional (vertical) script": "HanT_vert",
            "Hatian": "hat",
            "Hebrew": "heb",
            "Hebrew script": "Hebrew",
            "Hindi": "hin",
            "Hungarian": "hun",
            "Icelandic": "isl",
            "Indonesian": "ind",
            "Inuktitut": "iku",
            "Irish": "gle",
            "Italian": "ita",
            "Italian - Old": "ita_old",
            "Japanese": "jpn",
            "Japanese script": "Japanese",
            "Japanese (vertical)": "jpn_vert",
            "Japanese (vertical) script": "Japanese_vert",
            "Javanese": "jav",
            "Kannada": "kan",
            "Kannada script": "Kannada",
            "Kazakh": "kaz",
            "Khmer": "khm",
            "Khmer script": "Khmer",
            "Korean": "kor",
            "Korean (vertical)": "kor_vert",
            "Kurdish (Arabic)": "kur_ara",
            "Kyrgyz": "kir",
            "Lao": "lao",
            "Lao script": "Lao",
            "Latin": "lat",
            "Latin script": "Latin",
            "Latvian": "lav",
            "Lithuanian": "lit",
            "Luxembourgish": "ltz",
            "Macedonian": "mkd",
            "Malayalam": "mal",
            "Malayalam script": "Malayalam",
            "Malay": "msa",
            "Maltese": "mlt",
            "Maori": "mri",
            "Marathi": "mar",
            "Mongolian": "mon",
            "Myanmar script": "Myanmar",
            "Nepali": "nep",
            "Norwegian": "nor",
            "Occitan (post 1500)": "oci",
            "Old Georgian": "kat_old",
            "Oriya (Odia) script": "Oriya",
            "Oriya": "ori",
            "Pashto": "pus",
            "Persian": "fas",
            "Polish": "pol",
            "Portuguese": "por",
            "Punjabi": "pan",
            "Quechua": "que",
            "Romanian": "ron",
            "Russian": "rus",
            "Sanskrit": "san",
            "script and orientation": "osd",
            "Serbian (Latin)": "srp_latn",
            "Serbian": "srp",
            "Sindhi": "snd",
            "Sinhala script": "Sinhala",
            "Sinhala": "sin",
            "Slovakian": "slk",
            "Slovenian": "slv",
            "Spanish, Castilian - Old": "spa_old",
            "Spanish": "spa",
            "Sundanese": "sun",
            "Swahili": "swa",
            "Swedish": "swe",
            "Syriac script": "Syriac",
            "Syriac": "syr",
            "Tajik": "tgk",
            "Tamil script": "Tamil",
            "Tamil": "tam",
            "Tatar": "tat",
            "Telugu script": "Telugu",
            "Telugu": "tel",
            "Thaana script": "Thaana",
            "Thai script": "Thai",
            "Thai": "tha",
            "Tibetan script": "Tibetan",
            "Tibetan Standard": "bod",
            "Tigrinya": "tir",
            "Tonga": "ton",
            "Turkish": "tur",
            "Ukrainian": "ukr",
            "Urdu": "urd",
            "Uyghur": "uig",
            "Uzbek (Cyrillic)": "uzb_cyrl",
            "Uzbek": "uzb",
            "Vietnamese script": "Vietnamese",
            "Vietnamese": "vie",
            "Welsh": "cym",
            "Yiddish": "yid",
            "Yoruba": "yor",
        }

        # Load settings
        self.settings = Settings(self)

    def get_container_runtime(self) -> str:
        if platform.system() == "Linux":
            runtime_name = "podman"
        else:
            runtime_name = "docker"
        runtime = shutil.which(runtime_name)
        if runtime is None:
            raise Exception(f"{runtime_name} is not installed")
        return runtime

    def get_subprocess_startupinfo(self):  # type: ignore [no-untyped-def]
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            return startupinfo
        else:
            return None

    def install_container(self) -> Optional[bool]:
        """
        Make sure the podman container is installed. Linux only.
        """
        if self.is_container_installed():
            return True

        # Load the container into podman
        log.info("Installing Dangerzone container image...")

        p = subprocess.Popen(
            [self.get_container_runtime(), "load"],
            stdin=subprocess.PIPE,
            startupinfo=self.get_subprocess_startupinfo(),
        )

        chunk_size = 10240
        compressed_container_path = get_resource_path("container.tar.gz")
        with gzip.open(compressed_container_path) as f:
            while True:
                chunk = f.read(chunk_size)
                if len(chunk) > 0:
                    if p.stdin:
                        p.stdin.write(chunk)
                else:
                    break
        p.communicate()

        if not self.is_container_installed():
            log.error("Failed to install the container image")
            return False

        log.info("Container image installed")
        return True

    def is_container_installed(self) -> bool:
        """
        See if the podman container is installed. Linux only.
        """
        # Get the image id
        with open(get_resource_path("image-id.txt")) as f:
            expected_image_id = f.read().strip()

        # See if this image is already installed
        installed = False
        found_image_id = subprocess.check_output(
            [
                self.get_container_runtime(),
                "image",
                "list",
                "--format",
                "{{.ID}}",
                self.container_name,
            ],
            text=True,
            startupinfo=self.get_subprocess_startupinfo(),
        )
        found_image_id = found_image_id.strip()

        if found_image_id == expected_image_id:
            installed = True
        elif found_image_id == "":
            pass
        else:
            log.info("Deleting old dangerzone container image")

            try:
                subprocess.check_output(
                    [self.get_container_runtime(), "rmi", "--force", found_image_id],
                    startupinfo=self.get_subprocess_startupinfo(),
                )
            except:
                log.warning("Couldn't delete old container image, so leaving it there")

        return installed
