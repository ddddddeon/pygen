import argparse
from gen.project import Lang, ProjectType


def parse_args() -> tuple[Lang, str, ProjectType]:
    parser = argparse.ArgumentParser()
    parser.add_argument("lang")
    parser.add_argument("name")
    parser.add_argument("-l", "--lib", action="store_true")

    args = parser.parse_args()

    if not (args.lang and args.name):
        print("Usage: pygen <lang> <name> [-l | --lib]")
        exit(1)

    lang = Lang(args.lang)
    proj_type = ProjectType.LIBRARY if args.lib else ProjectType.EXECUTABLE

    return lang, args.name, proj_type
