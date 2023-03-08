import { useState } from 'react';
import Axios from 'axios';

import ChatComponent from './components/chat';
import BotIcon from './assets/image/bot.png';
import LogoIcon from './assets/image/logo.png';

import './App.css';

function SendMessage(data) {
	return new Promise(async (resolve, reject) => {
		try {
			const API_URL = process.env.REACT_APP_API_URL;
			const response = await Axios.post(API_URL, data);
			resolve(response.data.answer);
		} catch (error) {
			reject(error);
		}
	});
}

function App() {
	const [chatting_data, set_chatting_data] = useState('');
	const [loading, setLoading] = useState(false);
	const [messages, setMessages] = useState([]);

	const onChangeMessage = (e) => {
		set_chatting_data(e.target.value);
	};

	const onMessageKeyUp = (e) => {
		if (e.which === 13) {
			e.preventDefault();

			setLoading(true);

			const messageHistory = [
				...messages,
				{
					chatContent: chatting_data,
					humanChat: true,
				},
			];
			setMessages(messageHistory);

			SendMessage({
				chathistory:
					messageHistory.length < 5 ? messageHistory : messageHistory.slice(-5),
			})
				.then((res) => {
					// receiveMessage(res);
					setMessages([
						...messageHistory,
						{
							chatContent: res,
							humanChat: false,
						},
					]);
				})
				.catch((err) => {
					console.log(err);
				})
				.finally(() => {
					setLoading(false);
				});

			set_chatting_data('');
		}
	};

	let messageData = messages.map((message, index) => {
		return <ChatComponent {...message} key={index} />;
	});

	// const receiveMessage = (botMessage) => {
	// 	const messageHistory = [
	// 		...messages,
	// 		{
	// 			chatContent: botMessage,
	// 			humanChat: false,
	// 		},
	// 	];
	// 	console.log('messages', messages);
	// 	console.log('messageHistory', messageHistory);
	// 	setMessages(messageHistory);
	// };

	return (
		<div className="flex flex-col items-center justify-center w-screen min-h-screen bg-gray-100 text-gray-800 p-10 relative">
			<div className="md:flex md:flex-col flex-grow w-full md:max-w-[40%] bg-white shadow-xl rounded-lg overflow-hidden order-2">
				<div className="flex justify-center border-b-2 py-2">
					<img className="w-[30%]" src={LogoIcon} alt="logo"></img>
				</div>
				<div className="flex flex-col flex-grow p-4 overflow-auto md:h-0 h-[calc(100vh-14rem)]">
					<ChatComponent
						humanChat={false}
						chatContent={
							<>
								{/* <div>
									<img src={HelloEmoticon} alt="hello"></img>
								</div> */}
								<span className="text-sm leading-none">
									How are you? What can I help you? Please ask me.
								</span>
							</>
						}
					/>
					{messageData}
					{loading ? (
						<div className="flex w-full mt-2 space-x-3 max-w-xs">
							<div className="flex-shrink-0 h-10 w-10 rounded-full bg-gray-300">
								<img src={BotIcon} alt="bot"></img>
							</div>
							<div>
								<span className="text-sm text-gray-500 leading-none">
									typing...
								</span>
							</div>
						</div>
					) : null}
				</div>
				<div className="bg-gray-300 p-4 ">
					<input
						className="flex items-center h-10 w-full rounded px-3 text-sm"
						type="text"
						placeholder="Type your message…"
						onChange={onChangeMessage}
						onKeyUp={onMessageKeyUp}
						value={chatting_data}
					/>
				</div>
			</div>
			<div className="relative md:absolute text-center font-bold md:text-xl text-base md:top-[0px] md:right-[0px] md:w-[30vw] md:p-10 pb-10 order-1 items-center md:h-screen flex">
				<div className="w-full">
					<p>This is a Beta product Powered by AI. </p>
					<p>As of right now it will only give the "Stage" of the Project </p>
					<p className="w-[80%] mx-auto md:mt-20 mt-5">
						Questions must be frased as the following- "What is the stage of for
						customer X?"
					</p>
				</div>
			</div>
		</div>
	);
}

export default App;
