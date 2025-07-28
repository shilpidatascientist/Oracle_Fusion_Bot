from flask import Flask, request, jsonify
from langgraph_agent import *
app = Flask(__name__)


@app.route('/invoke/<user_message>', methods=['GET'])
def invoke_graph(user_message):
    try:
        result = supervisor.invoke({"messages": [("user", user_message)]},
                        config={"recursion_limit":2 * max_iterations + 1,**config})
    # Convert the markdown output to HTML
        #html_output = markdown.markdown(result['messages'][-1].content)
        #return jsonify({'response': markdown.markdown(html_output)})
        return jsonify({'response': result['messages'][-1].content})
    except Exception as e:
        return jsonify({'error': markdown.markdown(str(e))}), 500

if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=7000, use_reloader=False,
#             ssl_context=(
#             '/etc/ssl/certs/wildcard/fullchain.pem',
#             '/etc/ssl/certs/wildcard/privkey.key')
#     )
