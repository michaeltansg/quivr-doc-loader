pip uninstall -y langchain
pip install --upgrade git+https://github.com/michaeltansg/langchain@v0.0.208-ConfluencePatch
LANGCHAIN=$(pip freeze | grep "langchain @ ")
sed -i "s|langchain @ .*|$LANGCHAIN|" requirements.txt
