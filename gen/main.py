import os
from gen.util import parse_args
from gen.project import Project
from gen.project import ProjectType

def main():
    lang, name, proj_type = parse_args()
    if not proj_type:
        proj_type = ProjectType.EXECUTABLE
        
    project = Project(
        lang=lang,
        name=name,
        project_type=proj_type,
    )

    project.generate()


if __name__ == "__main__":
    main()
