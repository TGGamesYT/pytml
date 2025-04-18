import pytml

def example():
  pytml.setcontent("output", "recieved click")
  pytml.alert("why whould you click that")

pytml.defbutton("button", example)
pytml.run_app(port=5001)
