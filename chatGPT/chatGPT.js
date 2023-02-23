const API_KEY = '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';
$(document).ready(function () {
	// Handler for .ready() called.
	$('#chat_input_box').keyup(function (e) {
		if (e.which == 13 && $('#chat_input_box').val() !== '') {
			const humanChat = $('#chat_input_box').val();
			$('#chat_input_box').val('');
			$('#chatbox').append(`
      <div class="flex w-full mt-2 space-x-3 max-w-xs ml-auto justify-end">
        <div>
          <div class="bg-blue-600 text-white p-3 rounded-l-lg rounded-br-lg">
            <p class="text-sm">
              ${humanChat}
            </p>
          </div>
          <span class="text-xs text-gray-500 leading-none">2 min ago</span>
        </div>
        <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-300"></div>
      </div>
      `);

			$('#chatbox').append(`
      <div class="flex w-full mt-2 space-x-3 max-w-xs" id="loading">
        <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-300"></div>
        <div>
          <span class="text-xs text-gray-500 leading-none">loading...</span>
        </div>
      </div>
      `);

			callChatGPT(humanChat);
		}
	});
});

function callChatGPT(humanChat) {
	fetch(
		'https://45ce-2a00-23c7-ca06-7901-9950-842e-cf-444c.eu.ngrok.io/api/chat',
		{
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				question: humanChat,
			}),
		}
	)
		.then((response) => response.json())
		.then((response) => {
			const botChat = response.answer;
			$('#chatbox').append(`
      <div class="flex w-full mt-2 space-x-3 max-w-xs">
        <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-300"></div>
        <div>
          <div class="bg-gray-300 p-3 rounded-r-lg rounded-bl-lg">
            <p class="text-sm">
              ${botChat}
            </p>
          </div>
          <span class="text-xs text-gray-500 leading-none">2 min ago</span>
        </div>
      </div>
      `);
		})
		.finally(() => {
			$('#loading').remove();
		});
}
