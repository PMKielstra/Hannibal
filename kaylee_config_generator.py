print("""
{
    "commands": {""")

with open("artnames.txt") as artnamefile:
    artnames_list = artnamefile.readlines()
    for artname in artnames_list:
        print(f"\t\t\"hannibal, show me art by {artname[:-1]}\":\"echo 0{artname[:-1]} > searchkey\",".lower())
with open("artstyles.txt") as artstylefile:
    artstyles_list = artstylefile.readlines()
    for artstyle in artstyles_list:
        print(f"\t\t\"hannibal, show me {artstyle[:-1]} art\":\"echo 1{artstyle[:-1]} > searchkey\",".lower())
print("\t\t\"hannibal, shut down\":\"shutdown now\"")

print("""
    }
    "continuous": false,
    "history": false,
    "microphone": null,
    "interface": null,
    "valid_sentence_command": null,
    "invalid_sentence_command": null
}""")
