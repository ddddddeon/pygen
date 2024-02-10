import os
from .util import parse_args
from .project import Project


def main():
    lang, name, proj_type = parse_args()
    project = Project(
        lang=lang,
        name=name,
        project_type=proj_type,
    )

    project.generate()


if __name__ == "__main__":
    main()
