const { SlashCommandBuilder, SlashCommandAttachmentOption } = require('discord.js');
module.exports = {
	data: new SlashCommandBuilder().setName('ping').setDescription('Replies with Pong!').addAttachmentOption(new SlashCommandAttachmentOption().setName("attachment").setDescription("Attachment").setRequired(true)),
	async execute(interaction) {
		
		console.log(interaction.options.getAttachment("attachment")['url'])
        await interaction.reply("Check the console!")

		// const filter = (m) => m.author.id === interaction.user.id;
		
		// const q_collector = interaction.channel.createMessageCollector({
		// 	filter,
		// 	time: 60000,
		// 	max: 1,
		// });


		
		
		
		// q_collector.on('collect', async (m) => {
		// 	console.log(`Collected ${m.content}`);
		// 	console.log(`Full message: ${m}`);
		// 	//response_given = true;
		// 	await interaction.followUp('Collected input, please wait.');
		// 	// let { data, status, statusText } =  await axios.post(estimate_url, {'user_input': m.content});
			
		// 	//estimate = data;
		// 	//let { data, status, statusText } =  await axios.post(estimate_url, {'user_input': m.content}); 
		// 	//if (status == ) {}
		// 	//await interaction.followUp(`${data["kcal"]} calories, ${data["protein"]}g protein, and ${data["carbs"]}g carbs recorded.`);
		// 	//await axios.post(log_conversation_url, {});
		// });

		// q_collector.on('end', async (collected) => {
		// 	console.log(`Collected ${collected.size} messages`);
		// 	console.log(`Type: ${typeof (collected[0])}`);
		// 	console.log(`Actual value: ${collected[0]}`);
		// 	console.log(`Actual array: ${collected}`);
			
		// 	//Collected.attachments.values();
		// 	//console.log(`Collected this message: ${collected.attachments.values()} `);
		// });

	},
};