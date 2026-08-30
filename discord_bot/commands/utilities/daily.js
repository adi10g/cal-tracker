const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');
module.exports = {
	data: new SlashCommandBuilder().setName('daily').setDescription('Get daily macros overview!'),
	async execute(interaction) {
        //await interaction.deferReply(); 
        //await interaction.reply("Please wait");
        const get_macros_url = 'http://127.0.0.1:8000/get_macros_today/';
        
        let { data, status, statusText } =  await axios.get(get_macros_url);
		//await interaction.editReply('Describe your food in this thread within the next 5 minutes.');
		await interaction.reply(`${data["kcal"]} calories, ${data["protein"]}g protein, and ${data["carbs"]}g carbs consumed today.`);
	},
};