from dataclasses import dataclass
import yaml
import os
import glob

@dataclass()
class Config:
    #Questionnaire
    questionnaire=None
    questionnaire_path = "Questionnaire"
    questionnaire_title = "eHealth_questionnaire"

    # Rubric
    rubric=None
    rubric_path=""
    rubric_folder_path = "Rubric"
    rubric_title = "eHealth_icscore_rubric"

    # Default Setting
    language = "en"  # en, zh
    # NGROK_DOMAIN = "http://localhost:8080/"
    ngrok_domain = "http://eez114.ece.ust.hk:5000/"

    # mode
    debug_mode = False

    # Internal Param
    _current_session_id = None
    _redirect_FrontPage = False
    _redirect_TestPage = False

    def set_rubric(self):
        # Use Questionnaire with default language
        self.rubric_path = f"{os.path.join(self.rubric_folder_path, "_".join([self.rubric_title, self.language]))}.yaml"

        # Check if rubric with different language
        if not os.path.exists(self.rubric_path):
            # print("Check the corresponding questionnaire with different language...")
            all_rubrics = glob.glob("Rubric/*")
            self.rubric_path = next((rubric for rubric in all_rubrics if self.rubric_title in rubric), None)

        if self.rubric_path:
            with open(self.rubric_path, "r") as f:
                rubric = yaml.safe_load(f)
                self.rubric = rubric["RUBRIC"]
        else:
            self.rubric = None
            self.rubric_path = None

        # return RUBRIC, rubric_path

config = Config()
