from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Mapping

@dataclass(frozen=True)
class Paths:
    base: Path = Path("assets/prepared")

    # Input files
    inputs: Dict[str, str] = field(default_factory=lambda: {
        # EDUC
        "lfs_educ_regio":  "lfs_educ_regio_parsed.xlsx",
        "lfs_educ_sexage": "lfs_educ_sexage_parsed.xlsx",
        "lfs_educ_status": "lfs_educ_status_parsed.xlsx",
        # EMP
        "lfs_emp_regio":   "lfs_emp_regio_parsed.xlsx",
        "lfs_emp_sexage":  "lfs_emp_sexage_parsed.xlsx",
        # JOB
        "lfs_job_regio":   "lfs_job_regio_parsed.xlsx",
        "lfs_job_sexage":  "lfs_job_sexage_parsed.xlsx",
        "lfs_job_occup":   "lfs_job_occup_parsed.xlsx",
        # DEMO
        "lfs_occup_demo":  "lfs_occup_demo_parsed.xlsx",
        "lfs_sector_demo": "lfs_sector_demo_parsed.xlsx",
        # POPUL
        "lfs_popul_regio": "lfs_popul_regio_parsed.xlsx",
        "lfs_popul_status":"lfs_popul_status_parsed.xlsx",
        # STATUS
        "lfs_status_regio":"lfs_status_regio_parsed.xlsx",
        "lfs_status_sexage":"lfs_status_sexage_parsed.xlsx",
    })

    def file(self, key: str) -> Path:
        return self.base / self.inputs[key]


# Centralized column rename maps so we don’t repeat them in code
RENAME_MAPS: Mapping[str, Dict[str, str]] = {
    # JOB datasets
    "lfs_job_regio": {
        0:"Year", 1:"Region", 2:"TOT_EMP", 3:"NR_PERSONS_LOCAL_UNIT", 4:"BO", 5:"SECTOR",
        6:"SECTOR_SUB", 7:"TYPE_OCCUPATION", 8:"Main_Employment_Status", 9:"Employment_Distinction",
        10:"REASONS_PT", 11:"PERMANENCY_FOR_EMPLOYEES", 12:"PERMANENCY_FOR_EMPLOYEES_SUB",
        13:"REASONS_TEMP", 14:"HOURS_ACTUALLY_WORK", 15:"HOURS_ACTUALLY_WORK_SUB",
        16:"HOURS_USUAL_WORK", 17:"HOURS_USUAL_WORK_SUB", 18:"ATYPICAL_WORK", 19:"ATYPICAL_WORK_SUB",
        20:"Unit_of_Measure", 21:"Value"
    },
    "lfs_job_sexage": {
        0:"Year", 1:"Sex", 2:"Age_Group", 3:"TOT_EMP", 4:"NR_PERSONS_LOCAL_UNIT", 5:"BO", 6:"SECTOR",
        7:"SECTOR_SUB", 8:"TYPE_OCCUPATION", 9:"Main_Employment_Status", 10:"Employment_Distinction",
        11:"REASONS_PT", 12:"PERMANENCY_FOR_EMPLOYEES", 13:"PERMANENCY_FOR_EMPLOYEES_SUB",
        14:"REASONS_TEMP", 15:"HOURS_ACTUALLY_WORK", 16:"HOURS_ACTUALLY_WORK_SUB",
        17:"HOURS_USUAL_WORK", 18:"HOURS_USUAL_WORK_SUB", 19:"ATYPICAL_WORK", 20:"ATYPICAL_WORK_SUB",
        21:"Unit_of_Measure", 22:"Value"
    },
    "lfs_job_occup": {
        0:"Year", 1:"Occupation", 2:"TOT_EMP", 3:"NR_PERSONS_LOCAL_UNIT", 4:"BO", 5:"SECTOR", 6:"SECTOR_SUB",
        7:"Main_Employment_Status", 8:"Employment_Distinction", 9:"REASONS_PT",
        10:"PERMANENCY_FOR_EMPLOYEES", 11:"PERMANENCY_FOR_EMPLOYEES_SUB", 12:"REASONS_TEMP",
        13:"HOURS_ACTUALLY_WORK", 14:"HOURS_ACTUALLY_WORK_SUB", 15:"HOURS_USUAL_WORK",
        16:"HOURS_USUAL_WORK_SUB", 17:"ATYPICAL_WORK", 18:"ATYPICAL_WORK_SUB",
        19:"UNDERMP_PT_WORK", 20:"UNDERMP_PT_WORK_SUB", 21:"WORK_FOR_MORE_HOURS",
        22:"LOOKING_FOR_ANOTHER_JOB", 23:"HAVE_MORE_THAN_ONE_JOB_OR_BUSINESS",
        24:"WORK_WITHOUT_SSN", 25:"Unit_of_Measure", 26:"Value"
    },
    # DEMO
    "lfs_occup_demo": {
        0:"Year", 1:"TYPE_OCCUPATION", 2:"TOT_EMP", 3:"Sex", 4:"Sex_sub", 5:"Age_Group", 6:"Age_Group_sub",
        7:"Nationality", 8:"Education_Level_Main", 9:"Education_Level_Sub", 10:"Region", 11:"Regional_unit",
        12:"Region_1981", 13:"Region_1981_sub", 14:"Urbanization", 15:"Unit_of_Measure", 16:"Value"
    },
    "lfs_sector_demo": {
        0:"Year", 1:"SECTOR", 2:"TOT_EMP", 3:"Sex", 4:"Sex_sub", 5:"Age_Group", 6:"Age_Group_sub",
        7:"Nationality", 8:"Education_Level_Main", 9:"Education_Level_Sub", 10:"Region", 11:"Regional_unit",
        12:"Region_1981", 13:"Region_1981_sub", 14:"Urbanization", 15:"Unit_of_Measure", 16:"Value"
    },
    # EMP (final names after merge)
    "emp_final_names": {
        # After clean/merge we set columns directly in pipeline
    }
}
