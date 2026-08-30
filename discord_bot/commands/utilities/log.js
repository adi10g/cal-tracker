const { SlashCommandBuilder, SlashCommandAttachmentOption } = require('discord.js');
const axios = require('axios');

module.exports = {
	data: new SlashCommandBuilder().setName('log').setDescription('Log a food item').addAttachmentOption(new SlashCommandAttachmentOption().setName("attachment").setDescription("Attachment").setRequired(true)),
	async execute(interaction) {
		// await interaction.deferReply(); 
		// await interaction.editReply('Describe your food in this thread within the next 5 minutes.');
		const filter = (m) => m.author.id === interaction.user.id;
        const gen_q_url = 'http://127.0.0.1:8000/generate_questions/';
        const estimate_url = 'http://127.0.0.1:8000/final_estimate/';
        const log_conversation_url = 'http://127.0.0.1:8000/log_conversation/';

        let q_asked = false;
        let response_given = false;
        
        async function conversation() {
        
            await interaction.reply("Please wait for some questions. If no response, I'll make my best guess!");
            

            let { data, status, statusText } =  await axios.post(gen_q_url, {'user_input': interaction.options.getAttachment("attachment")['url']});

            // do we have to download it? try sending wo

            if (status == 200) {
                await interaction.followUp(data['questions_txt']);
                q_asked = true; 
            } else {
                await interaction.followUp('Try again, backend error.'); 
                return;
            }


            const q_collector = await interaction.channel.createMessageCollector({
                filter,
                time: 60000,
                max: 1,
            });


            q_collector.on('collect', async (m) => {
                console.log(`Collected ${m.content}`);
                response_given = true;
                await interaction.followUp('Collected input, please wait.');
                let { data, status, statusText } =  await axios.post(estimate_url, {'user_input': m.content});
                
                //estimate = data;
                //let { data, status, statusText } =  await axios.post(estimate_url, {'user_input': m.content}); 
                //if (status == ) {}

                await interaction.followUp(`${data["kcal"]} calories, ${data["protein"]}g protein, and ${data["carbs"]}g carbs recorded.`);

                try {
                    await axios.post(log_conversation_url, {});
                } catch (error) {
                    console.error(error);
                    // Expected output: ReferenceError: nonExistentFunction is not defined
                    // (Note: the exact output may be browser-dependent)
                }
            });

            q_collector.on('end', async (collected) => {
                if (q_asked && !response_given){
                    //console.log('');
                    await interaction.followUp('Time is up!'); 
                } else if (q_asked && response_given) {
                        // debug if this works or not? 
                    // supabase logging
                    
                    console.log('Question response, recieved logging'); 
                } else {
                    console.log('Q1 collector ended but q1 has not been asked.'); 
                    await interaction.followUp('Try again, backend error.'); 
                    return;
                }
                
            });
        }



        conversation(); 





        // async function conversation() {
            
             

        //     const collector = interaction.channel.createMessageCollector({
        //         filter,
        //         time: 60000,
        //         max: 1,
        //     });


        //     await collector.on('collect', async (m) => {
        //         console.log(`Main collector on event`);
                
        //         await m.reply('Collected input, please wait.');

                
        //         //console.log(msg); 
        //         let { data, status, statusText } =  await axios.post(gen_q_url, {'user_input': m.content});
        //         console.log(status, statusText);
        //         console.log(data);
        //         // let response = await axios.post(url, {'user_input': msg}); // replace w/ m.content?
        //         // console.log(m); 
        //         // let collectedString = getGPTOutput(m.content);

        //         if (status == 200) {
        //             await interaction.followUp(data['questions_txt']);
        //             q_asked = true; 
        //         } else {
        //             await interaction.followUp('Try again, backend error.'); 
        //             return;
        //         }

        //     });

        //     collector.on('end', async (collected) => {
        //         console.log(`Main collector end event, collected.size: ${collected.size}`);

                
        //         if (collected.size) {
                    
        //             const q_collector = await interaction.channel.createMessageCollector({
        //                 filter,
        //                 time: 60000,
        //                 max: 1,
        //             });


        //             q_collector.on('collect', async (m) => {
        //                 console.log(`Collected ${m.content}`);
        //                 response_given = true;
        //                 await interaction.followUp('Collected input, please wait.');
        //                 let { data, status, statusText } =  await axios.post(estimate_url, {'user_input': m.content});
                        
        //                 //estimate = data;
        //                 //let { data, status, statusText } =  await axios.post(estimate_url, {'user_input': m.content}); 
        //                 //if (status == ) {}

                        

                        



        //                 await interaction.followUp(`${data["kcal"]} calories, ${data["protein"]}g protein, and ${data["carbs"]}g carbs recorded.`);
        //                 await axios.post(log_conversation_url, {});
        //             });

        //             q_collector.on('end', async (collected) => {
        //                 if (q_asked && !response_given){
        //                     //console.log('');
        //                     await interaction.followUp('Time is up!'); 
        //                 } else if (q_asked && response_given) {
        //                      // debug if this works or not? 
        //                     // supabase logging
                            
        //                     console.log('Question response, recieved logging'); 
        //                 } else {
        //                     console.log('Q1 collector ended but q1 has not been asked.'); 
        //                     await interaction.followUp('Try again, backend error.'); 
        //                     return;
        //                 }
                        
        //             });
                    
        //         }
        //         //await interaction.followUp('Collected input, please wait.'); 
        //     });

            
            
        // }

        // conversation(); 

	},
};