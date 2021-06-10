# STEVE
The one and only Syntax Tree parsEr anVd buildEr.
Generate 3D models of abstract syntax trees. Perhaps make them into a hat.

## Files in this Repo:
1. `sample_programs`: Some simple Python scripts I used for testing the system
2. `ast_samples`: Some sample AST text files, including STEVE's entire AST
3. `ast_rhino.zip`: The Rhino environment I worked in. Probably has some fully-baked ASTs lying around in it, but if you want to start from scrath you just need to draw some polygons and connect them to the Curve inputs of the `parse_ast` Grasshopper file.
4. `parse_ast.gh`: The full STEVE system, including the snippet used to test moving polygons around and drawing edges. To use it, set the value of the `Text` input to the path of an AST text file you want to fabricate.
5. `full_parse_gen_logic.py`: All the code from STEVE's brain. Probably won't run outside the Grasshopper environment, I just included it separately to make it easier to examine.

## Other Notes:
If you want to try STEVE with a Python program of your own, be sure to download the `astdump` helper to get AST text files of the right format! 
https://pypi.org/project/astdump/

