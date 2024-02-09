import os
from util import parse_args
from project import Project

if __name__ == "__main__":
    lang, name, proj_type = parse_args()
    project = Project(
        lang=lang,
        name=name,
        project_type=proj_type,
    )
    print(project)

    project.generate()
