import argparse
from .project import Lang, ProjectType


def parse_args() -> tuple[Lang, str, ProjectType]:
    parser = argparse.ArgumentParser()
    parser.add_argument("lang")
    parser.add_argument("name")
    parser.add_argument("proj_type", nargs="?", default="bin")
    args = parser.parse_args()

    if not (args.lang and args.name):
        print("Usage: pygen <lang> <name> [-l]")
        exit(1)

    lang = Lang(args.lang)
    proj_type = ProjectType(args.proj_type)

    return lang, args.name, proj_type
