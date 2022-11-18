import discord
import asyncio
import datetime
from discord import app_commands


#Initialising the bot
class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False
    
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        print("Connected Successfully!")

client = aclient()
tree = app_commands.CommandTree(client)


#Global ID's for officers in both UCF and Test server. 
#This is to remove the vunrability of an NCO creating a new role called 'Officer' and giving it to themselves. Not done for NCO as enlisted can't alter roles anyway
UCFOfficer = 487335479042375701
TestOfficer = 1026948837073494037


#Inducts a member into the clan via giving the appropriate roles and changing their nickname
@tree.command(name = "induct", description = "Inducts a member into the clan")
@discord.app_commands.checks.has_any_role("NCO", UCFOfficer, TestOfficer)
async def induct(interaction:discord.Interaction, inductee:discord.User, steamname:str):
    guild = interaction.guild
    await interaction.response.defer()

    #Changes nickname
    await inductee.edit(nick="[UCF] " + steamname)
    
    #Changes roles
    addRoleList = ['Recruit','United Colonial Front','Basic Training Not Complete', '⁣         ⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⤙ Sections ⤚ ⁣⁣⁣⁣⁣⁣⁣⁣        ⁣⁣⁣⁣⁣⁣⁣⁣  ⁣⁣⁣⁣⁣⁣⁣⁣', '⁣         ⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⤙  Other  ⤚ ⁣⁣⁣⁣⁣⁣⁣⁣        ⁣⁣⁣⁣⁣⁣⁣⁣  ⁣⁣⁣⁣⁣⁣⁣⁣', '⁣         ⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⤙  Medals  ⤚ ⁣⁣⁣⁣⁣⁣⁣⁣        ⁣⁣⁣⁣⁣⁣⁣⁣  ⁣⁣⁣⁣⁣⁣⁣⁣', '⁣         ⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⁣⤙   Pings   ⤚ ⁣⁣⁣⁣⁣⁣⁣⁣        ⁣⁣⁣⁣⁣⁣⁣⁣  ⁣⁣⁣⁣⁣⁣⁣⁣']
    for role in addRoleList:
        await inductee.add_roles(discord.utils.get(guild.roles, name=role), reason="Inducted by UCF Bot.")
    await inductee.remove_roles(discord.utils.get(guild.roles, name='Unassigned'), reason="Inducted by UCF Bot.")
    
    #Sends welcome message in general chat
    await discord.utils.get(guild.channels, name='general-chat').send(inductee.mention + " Welcome! Be sure to check out " + discord.utils.get(guild.channels, name='must-read').mention 
                                                                                       + " for the server rules and FAQ's. Also check " + discord.utils.get(guild.channels, name='announcements').mention
                                                                                       + " for upcoming operations and other big events. Look in " + discord.utils.get(guild.channels, name='training-forecast').mention 
                                                                                       + " for basic training which will teach you the basics of the game & let you rank up past private. We also have " + discord.utils.get(guild.channels, name='advanced-training').mention 
                                                                                       + " for learning the more complex aspects of the game, please use " + discord.utils.get(guild.channels, name='auto-assign').mention 
                                                                                       + " to get notified for when training that you are interested in takes place. If you have any questions, please just ask!")
    
    #Sends confirmation message
    await interaction.followup.send('Successfully Inducted: ' + str(inductee.mention))
    print("Inducted member: " + str(inductee) + " by: " + str(interaction.user))
@induct.error
async def inductError(interaction: discord.Interaction, error: Exception):
    await errorHandling(interaction, error, "NCO/Officer")


#Gives all users with a specified role another specified role. May take a very long time to run (10 minutes+) due to avoiding getting rate limited
@tree.command(name = "massallocaterole", description = "Gives a role to all members with a certain role. May take a long time to execute. Officer use only.")
@discord.app_commands.checks.has_any_role(UCFOfficer, TestOfficer)
async def massallocaterole(interaction:discord.Interaction, hasrole: discord.Role, giverole: discord.Role):
    guild = interaction.guild
    await interaction.response.defer()
    
    #Adds roles. May take a long time.
    count = 0
    hasRoleList = hasrole.members
    for member in hasRoleList:
        await member.add_roles(giverole, reason="Given via UCF bot in mass assign")
        await asyncio.sleep(0.5)
        count = count + 1
    await interaction.followup.send("Successfully mass allocated roles to: " + str(count) + " members")
@massallocaterole.error
async def massallocateroleError(interaction: discord.Interaction, error: Exception):
    await errorHandling(interaction, error, "Officer")


#Begins the bi-weekly promotions meeting. IMPORTANT: This has not been implemented yet "Prints out the data stored in graphs and numbers", and purges unassinged members that have been inactive since the last meeting (2 weeks)
@tree.command(name = "startmeeting", description = "Starts the promotions meeting. Prints info and purges unassigned. Officer use only")
@discord.app_commands.checks.has_any_role(UCFOfficer, TestOfficer)
async def startmeeting(interaction:discord.Interaction):
    guild = interaction.guild
    await interaction.response.defer()

    voteList.clear()

    #Purges all members that have the unassigned role and have been inactive for 2 weeks or more
    unassigned = discord.utils.get(guild.roles, name="Unassigned")
    for member in unassigned.members:
        timeSinceJoined = datetime.datetime.now() - member.joined_at.replace(tzinfo=None)
        if timeSinceJoined.days > 14:
            await member.kick()
            await asyncio.sleep(0.5)
    
    #Prints confimation message
    await interaction.followup.send("Meeting started!")
@startmeeting.error
async def startmeetingError(interaction: discord.Interaction, error: Exception):
    await errorHandling(interaction, error, "Officer")


#Ends the bi-weekly promotions meeting. Gives roles for all members voted on for both promotions and medals, and prints summary of promotees and medal recipients. Also updates rank and medal structures. 
@tree.command(name = "endmeeting", description = "Ends the promotions meeting. Promotes/gives medals for all members voted on. Officer use only")
@discord.app_commands.checks.has_any_role(UCFOfficer, TestOfficer)
async def endmeeting(interaction:discord.Interaction):
    guild = interaction.guild
    await interaction.response.defer()

    #Creates printable list of all promotees. Also sets promotee nicknames

    #Initialising variables
    promoteeList = []
    prefixDict = {'Recruit': '[UCF', 'Private': '+[UCF', 'Veteran': '++[UCF', 'Legionnaire': '+++[UCF',
                  'Pioneer': '*[UCF☆', 'Lance Corporal': '*[UCF☆', 'Corporal': '*[UCF☆', 'Assistant Facility Master': '*[UCF☆', 'Assistant Quartermaster': '*[UCF☆', 'Sergeant': '*[UCF☆', 'First Sergeant': '*[UCF☆', 'Sergeant Major': '*[UCF☆',
                  'Officer Cadet': '**[UCF★', 'Second Lieutenant': '**[UCF★', 'Lieutenant': '**[UCF★', 'Captain': '**[UCF★', 'Quartermaster': '**[UCF★',
                  'Sub-Commander': '***[UCF★', 'Commander': '***[UCF★', 'Supreme Commander': '***[UCF★'}
    ncoRoles = ["First Sergeant", "Sergeant", "Assistant Quartermaster", "Assistant Facility Master", "Corporal", "Lance Corporal"]
    officerRoles = ["Supreme Commander", "Commander", "Sub-Commander", "Quartermaster", "Facility Master", "Captain", "Lieutenant", "Second Lieutenant", "Officer Cadet", "Sergeant Major"]

    #Setting nickname of sucsessful promotees. Adds promotees to list for printing
    for vote in voteList:
        #Refreshing vote message so the bot knows about reactions taken place after initial recording of the message. Doesnt update if message was deleted
        try:
            vote[0] = await vote[0].fetch()
            #Checks if yes votes outnumber no votes
            if vote[0].reactions[0].count > vote[0].reactions[1].count:
                #Adds promotee to list for later use
                promotee = (vote[1], vote[2])
                promoteeList.append(promotee)

                #Changes nickname
                splitNick = list(vote[1].nick)
                for char in list(splitNick):
                    if not char == ']':
                        splitNick.remove(char)
                    else:
                        break
                suffixNick = ''.join(splitNick)
                await vote[1].edit(nick = prefixDict[vote[2].name] + suffixNick)
        except:
            pass

    #Updates roles
    for promotee in promoteeList:
        #Avoids getting rate limited
        await asyncio.sleep(0.5)

        #Removes previous rank, adds new
        await promotee[0].remove_roles(promotee[0].roles[-1], reason="Promoted via vote by UCF Bot")
        await promotee[0].add_roles(promotee[1], reason="Promoted via vote by UCF Bot")

        #Gives NCO role
        if promotee[1].name in ncoRoles:
            await promotee[0].add_roles(discord.utils.get(guild.roles, name='NCO'), reason="Promoted via vote by UCF Bot")
        #Gives Officer role
        if promotee[1].name in officerRoles:
            await promotee[0].add_roles(discord.utils.get(guild.roles, name='Officer'), reason="Promoted via vote by UCF Bot")
            await promotee[0].remove_roles(discord.utils.get(guild.roles, name='NCO'), reason="Promoted via vote by UCF Bot")


    #Gets string of promotees, with ranks seperating themm
    promoteeDict = dict(promoteeList)
    sortedList = sortMemberSet(set([row[0] for row in promoteeList]))
    promoteeString = ""
    previousRank = ''
    for promotee in sortedList:
        if not promoteeDict[promotee] == previousRank:
            promoteeString = promoteeString + "\n" + promoteeDict[promotee].mention + "\n\n"

        promoteeString = promoteeString + promotee.mention + "\n"
        previousRank = promoteeDict[promotee]

    #Creates printable list of all medal recipients

    #Medal recipients are appended into the lists for each medal
    medalDict = {"Phalera of the United Colonial Front": [], "Phalera of the Legion": [], "Phalera of the Green Banner": [], 
                 "Distinguished Service Medal Class 1": [], "Distinguished Service Medal Class 2": [], "Distinguished Service Medal Class 3": [], 
                 "Order of the Green Cross Class 1": [], "Order of the Green Cross Class 2": [],
                 "Patch of the Architect": [], "Patch of the Foreman": [],
                 "Sash of the Harvester": [], "Sash of the Sledge": [], "Sash of the Hammer": [],
                 "Ribbon of the Custodian": [], "Ribbon of the Silent Workhorse": [],
                 "Badge of Strategy": [], "Badge of Valour": [], "Badge of the Provisioner": [], "Badge of the Saboteur": [], "Badge of the Sapper": []}

    with open('medal_votes.txt', 'r') as file:
        medalNomineeList = file.readlines()
        #Runs for every line in file. Each nominee object contains (all stored as strings) message, memberID, medalname
        for nominee in medalNomineeList:
            nominee = nominee.split(",")
            #Gets message via converting the string stored inside the file into a message object
            message = await getMessageFromFile(nominee[0], interaction)
            
            #Fails if message was deleted
            try:
                message = await message.fetch()
                #Checks if vote has passed
                if message.reactions[0].count > message.reactions[1].count:
                    medalDict[nominee[2]].append(nominee[1])
            except:
                pass

    #Creates string to be printed of medal recipients, with medals seperating them
    medalRecipients = []
    medalString = ""
    for medal in medalDict:
        #Runs if medal has any recipients
        if medalDict[medal]:
            #Adding medal to string
            medalString = medalString + "\n" + discord.utils.get(guild.roles, name = medal).mention + "\n\n"

            #Turning list of ID's into list of member objects
            unsortedMemberList = []
            for memberID in medalDict[medal]:
                member = await guild.fetch_member(memberID)
                unsortedMemberList.append(member)
                medalRecipients.append([member, discord.utils.get(guild.roles, name = medal)])

            #Sorting member list and then adding sorted members to string
            sortedMedalList = sortMemberSet(set(unsortedMemberList))
            for member in sortedMedalList:
                medalString = medalString + member.mention + "\n" 

    #Sending message to user
    await interaction.followup.send(promoteeString + "\n" + medalString)
    await interaction.channel.send("Ranks:\n```\n" + promoteeString + "\n```")
    await interaction.channel.send("Medals:\n```\n" + medalString + "\n```")

    #Gives medals. Runs after response message, so the message can be sent to the user faster, as the message does not need to know that the medals have actually been delivered
    for recipient in medalRecipients:
        await recipient[0].add_roles(recipient[1], reason = "Given during promotion meeting")
        await asyncio.sleep(0.5)

    #Resets votes
    voteList.clear()
    partialVoteList.clear()
    open("medal_votes.txt", "w").close()

    #Updates medal and rank structure messages
    await editRankStructure(interaction)
    await editMedalStructure(interaction)  
@endmeeting.error
async def endmeetingError(interaction: discord.Interaction, error: Exception):
    await errorHandling(interaction, error, "Officer")


#Global variables for communicating between votes
voteList = []
partialVoteList = []
#Starts promotion vote for a member. Checks if user has basic training. NCO+ promotion only possible by Officers, NCO's can do enlisted promotions
@tree.command(name = "vote", description = "Starts a promotion vote for a member. Only officers can promote to NCO+")
@discord.app_commands.checks.has_any_role("NCO", UCFOfficer, TestOfficer)
async def vote(interaction:discord.Interaction, promotee:discord.User, rank:discord.Role):
    guild = interaction.guild

    #Initialising variables
    ncoPromotionList = ['Recruit', 'Private', 'Veteran', 'Legionnaire']

    #Checks if user has access level to start the vote
    if rank.name in ncoPromotionList or discord.utils.get(guild.roles, id = UCFOfficer) in interaction.user.roles or discord.utils.get(guild.roles, id = TestOfficer) in interaction.user.roles:
        #Checks user has basic training if being promoted from private
        if promotee.roles[-1] == discord.utils.get(guild.roles, name='Private'):
            if discord.utils.get(guild.roles, name='Basic Training Complete') in promotee.roles:
                pass
            else:
                await interaction.response.send_message(promotee.mention + " does not have basic training!")
                return 
        
        #Checks if the vote is a duplicate
        if [promotee, rank] in partialVoteList:
            await interaction.response.send_message("Duplicate vote!")
            return

        #Prints message of user to be voted for, and adds emojis for voting
        await interaction.response.send_message(promotee.mention + " to " + rank.mention)
        voteMessage = await interaction.original_response()
        await voteMessage.add_reaction("✅")
        await voteMessage.add_reaction("❌")

        #Adds vote to list to be used in endVoting function
        voteList.append([voteMessage, promotee, rank])
        partialVoteList.append([promotee, rank])

    else:
        await interaction.response.send_message("You do not have the permissions to promote a member to that rank. Requires: Officer")
@vote.error
async def voteError(interaction: discord.Interaction, error: Exception):
    await errorHandling(interaction, error, "NCO/Officer")


#Starts a vote for a member to get a medal. Appends vote message to a file to be read with endmedalvoting
@tree.command(name = "medalvote", description = "Starts a vote for a member to get a medal")
@discord.app_commands.checks.has_any_role("NCO", UCFOfficer, TestOfficer)
async def medalvote(interaction:discord.Interaction, promotee:discord.User, medal:discord.Role, reason: str):
    medalList = ["Phalera of the United Colonial Front", "Phalera of the Legion", "Phalera of the Green Banner", 
                 "Distinguished Service Medal Class 1", "Distinguished Service Medal Class 2", "Distinguished Service Medal Class 3", 
                 "Order of the Green Cross Class 1", "Order of the Green Cross Class 2",
                 "Patch of the Architect", "Patch of the Foreman",
                 "Sash of the Harvester", "Sash of the Sledge", "Sash of the Hammer",
                 "Ribbon of the Custodian", "Ribbon of the Silent Workhorse",
                 "Badge of Strategy", "Badge of Valour", "Badge of the Provisioner", "Badge of the Saboteur", "Badge of the Sapper"]

    #Checks the member is being given a medal, and not some other role
    if medal.name in medalList:
        #Prints message of user to be voted for, and adds emojis for voting
        await interaction.response.send_message(promotee.mention + " for " + medal.mention + ": " + reason)
        voteMessage = await interaction.original_response()
        await voteMessage.add_reaction("✅")
        await voteMessage.add_reaction("❌")

        #Appends to file containing all medal votes
        with open('medal_votes.txt', 'a') as file:
            file.write(str(voteMessage) + "," + str(promotee.id) + "," + str(medal.name) + ", \n")  
    else:
        await interaction.response.send_message("That is not a medal.")
@medalvote.error
async def medalvoteError(interaction: discord.Interaction, error: Exception):
    await errorHandling(interaction, error, "NCO/Officer")


#Updates the rank structure. Can create a new message, or update the old one
@tree.command(name = "updatemedalstructure", description = "Manually updates/prints the medal structure")
@discord.app_commands.checks.has_any_role("NCO", UCFOfficer, TestOfficer)
async def updatemedalstructure(interaction:discord.Interaction, newmessage: bool):
    guild = interaction.guild
    await interaction.response.defer()

    #Checks for if a new message is wanted, or the old one should be updated
    if newmessage == True:
        #Sends message in same channel that the interaction took place
        splitMedalStructure = await generateMedalStructure(interaction)
        
        messageOne = await interaction.channel.send(splitMedalStructure[0])
        messageTwo = await interaction.channel.send(splitMedalStructure[1])

        #Saves the message to a txt file as a string
        with open('medal_structure_message.txt', 'w') as file:
            file.write(str(messageOne) + "\n" + str(messageTwo))
    else:
        #Edits message stored in the medal structure file
        await editMedalStructure(interaction)

        #Sends confirmation message
        await interaction.followup.send("Successfully Updated!")
@updatemedalstructure.error
async def updatemedalstructureError(interaction: discord.Interaction, error: Exception):
    await errorHandling(interaction, error, "NCO/Officer")


#Edits the rank structure message. Can be called manually using above function, or can be called automatically
async def editMedalStructure(interaction):
    guild = interaction.guild

    #Initialising variables
    message = ""

    #Reads from medal structure file
    with open('medal_structure_message.txt', 'r') as file:
        #Gets message via converting the string stored inside the file into a message object
        messageStringList = file.readlines()
        messageOne = await getMessageFromFile(messageStringList[0], interaction)
        messageTwo = await getMessageFromFile(messageStringList[1], interaction)

    #Updates message
    splitMedalStructure = await generateMedalStructure(interaction)
    await messageOne.edit(content = splitMedalStructure[0])
    await messageTwo.edit(content = splitMedalStructure[1])


#Generates the medal structure message
async def generateMedalStructure(interaction):
    guild = interaction.guild

    #Initialising variables
    medalStructure = ""
    medalDict = {"Phalera of the United Colonial Front": "Phalera_of_the_UCF", "Phalera of the Legion": "Phalera_of_the_Legion", "Phalera of the Green Banner": "Phalera_of_the_Green_Banner", 
                 "Distinguished Service Medal Class 1": "DSMC1", "Distinguished Service Medal Class 2": "DSMC2", "Distinguished Service Medal Class 3": "DSMC3", 
                 "Order of the Green Cross Class 1": "Order_of_the_Green_Cross_Class_1", "Order of the Green Cross Class 2": "Order_of_the_Green_Cross_Class_2",
                 "Patch of the Architect": "", "Patch of the Foreman": "",
                 "Sash of the Harvester": "", "Sash of the Sledge": "", "Sash of the Hammer": "",
                 "Ribbon of the Custodian": "", "Ribbon of the Silent Workhorse": "",
                 "Badge of Strategy": "", "Badge of Valour": "", "Badge of the Provisioner": "", "Badge of the Saboteur": "", "Badge of the Sapper": ""}

    medalList = list(medalDict.keys())
    
    #Runs for every medal
    for medal in medalList:
        #Adds medal header line
        medalID = discord.utils.get(guild.roles, name=medal)
        memberList = medalID.members
        medalStructure = medalStructure + "\n\n" + medalID.mention + " "

        #Adds emoji, if it exists
        if discord.utils.get(guild.emojis, name=medalDict[medal]):
            medalStructure = medalStructure + str(discord.utils.get(guild.emojis, name=medalDict[medal]))
        medalStructure = medalStructure + "\n"

        #Adds sorted list of all members of the rank. If there is no members, adds 'Empty!'
        if memberList:
            sortedMemberList = sortMemberSet(set(memberList))
            for member in sortedMemberList:
                medalStructure = medalStructure + "\n" + member.mention
        else:
            medalStructure = medalStructure + "Empty!"   

    #Splitting message into two where Order of Green Cross 1 is
    splitMedalStructure = medalStructure.split("<@&903686553392537621>")
    splitMedalStructure[1] = "<@&903686553392537621>" + splitMedalStructure[1]

    return splitMedalStructure

    
#Updates the rank structure. Can create a new message, or update the old one
@tree.command(name = "updaterankstructure", description = "Manually updates/prints the rank structure. Automatically done after every meeting")
@discord.app_commands.checks.has_any_role("NCO", UCFOfficer, TestOfficer)
async def updaterankstructure(interaction:discord.Interaction, newmessage: bool):
    guild = interaction.guild

    #Checks for if a new message is wanted, or the old one should be updated
    if newmessage == True:
        #Sends message in same channel that the interaction took place
        message = await interaction.channel.send(await generateRankStructure(interaction))

        #Saves the message to a txt file as a string
        with open('rank_structure_message.txt', 'w') as file:
            file.write(str(message))
    else:
        #Edits message stored in the rank structure file
        await editRankStructure(interaction)

        #Sends confirmation message
        await interaction.response.send_message("Successfully Updated!")
@updaterankstructure.error
async def updaterankstructureError(interaction: discord.Interaction, error: Exception):
    await errorHandling(interaction, error, "NCO/Officer")


#Edits the rank structure message. Can be called manually using above function, or can be called automatically
async def editRankStructure(interaction):
    guild = interaction.guild

    #Initialising variables
    message = ""

    #Reads from rank structure file
    with open('rank_structure_message.txt', 'r') as file:
        #Gets message via converting the string stored inside the file into a message object
        messageString = file.readline()
        message = await getMessageFromFile(messageString, interaction)

    #Updates message
    await message.edit(content = await generateRankStructure(interaction))


#Generates the rank structure message
async def generateRankStructure(interaction):
    guild = interaction.guild

    #Initialising variables
    rankStructure = ""
    rankList = ["Supreme Commander", "Commander", "Sub-Commander", "Quartermaster", "Facility Master", "Captain", "Lieutenant", "Second Lieutenant", "Officer Cadet", "Sergeant Major", "First Sergeant", "Sergeant", "Assistant Quartermaster", "Assistant Facility Master", "Corporal", "Lance Corporal"]
    capacityDict = {'Pioneer': '*N/A*', 'Lance Corporal': '*8 Slots*', 'Corporal': '*6 Slots*', 'Assistant Facility Master': '*2 Slots*', 'Assistant Quartermaster': '*4 Slots*', 'Sergeant': '*2 Slots*', 'First Sergeant': '*2 Slots*', 'Sergeant Major': '*1 Slot*',
                   'Officer Cadet': '*Trial Rank*', 'Second Lieutenant': '*2 Slots*', 'Lieutenant': '*2 Slots*', 'Captain': '*2 Slots*', 'Facility Master': '*1 Slot*', 'Quartermaster': '*1 Slot*',
                   'Sub-Commander': '*Reserve*', 'Commander': '*1 Slot*', 'Supreme Commander': '*1 Slot*'}
    
    #Runs for every NCO+ rank
    for rank in rankList:
        #Adds line of mentioned rank and its slots
        rankID = discord.utils.get(guild.roles, name=rank)
        memberList = rankID.members
        rankStructure = rankStructure + "\n\n" + rankID.mention + " - " + capacityDict[rank] + " - "

        #Adds sorted list of all members of the rank. If there is no members, adds 'Empty!'
        if memberList:
            sortedMemberList = sortMemberSet(set(memberList))
            for member in sortedMemberList:
                rankStructure = rankStructure + member.mention + " "
        else:
            rankStructure = rankStructure + "Empty!"   
    return rankStructure


#Takes a snapshot of training channel and gives all members basic training complete roles. Also sends list of trainees for pasting into report
@tree.command(name = "basictraining", description = "Gives all trainees basic training role. Also prints list of trainees")
@discord.app_commands.checks.has_any_role("NCO", UCFOfficer, TestOfficer)
async def basictraining(interaction:discord.Interaction):
    guild = interaction.guild
    await interaction.response.defer()

    #Gets training voice members
    traineeSet = set()
    trainingVoice = discord.utils.get(guild.voice_channels, name='Training-VC')
    for trainee in trainingVoice.members:
        traineeSet.add(trainee)
    traineeSet.remove(interaction.user) #Removes training host from set
    sortedList = sortMemberSet(traineeSet)

    #Returns trainees to user
    responseMessage = generateReport(sortedList)
    await interaction.followup.send(responseMessage)
    await interaction.channel.send("```\n" + responseMessage + "\n```")

    #Adds and removes roles
    trainingComplete = discord.utils.get(guild.roles, name='Basic Training Complete')
    trainingNotComplete = discord.utils.get(guild.roles, name='Basic Training Not Complete')
    for trainee in sortedList:
        await asyncio.sleep(0.5) #Avoids getting rate limited
        await trainee.add_roles(trainingComplete, reason="Added by UCF Bot")
        await trainee.remove_roles(trainingNotComplete, reason="Removed by UCF Bot")

    print("Basic training complete for: " + str(sortedList) + " by: " + str(interaction.user))
@basictraining.error
async def basictrainingError(interaction: discord.Interaction, error: Exception):
    await errorHandling(interaction, error, "NCO/Officer")


#Takes a snapshot of a specifed voice channel and prints it out
@tree.command(name = "voicesnapshot", description = "Prints a list of all members currently in a specified voice channel")
@discord.app_commands.checks.has_any_role("NCO", UCFOfficer, TestOfficer)
async def voicesnapshot(interaction:discord.Interaction, voicechannel:discord.VoiceChannel):
    guild = interaction.guild
    await interaction.response.defer()

    #Gets voice members
    voiceSet = set()
    for member in voicechannel.members:
        voiceSet.add(member)
    sortedList = sortMemberSet(voiceSet)
    #Retuns voice members to user
    responseMessage = generateReport(sortedList)
    await interaction.followup.send(responseMessage)
    await interaction.channel.send("```\n" + responseMessage + "\n```")

    print("Snapshot taken for channel: " + str(voicechannel) + " by: " + str(interaction.user))
@voicesnapshot.error
async def voicesnapshotError(interaction: discord.Interaction, error: Exception):
    await errorHandling(interaction, error, "NCO/Officer")


#Global variables for use in communicating between "operationstart" and "operationend" functions
operationStatus = False
memberSet = set()


#Records the members that join any operation voice channels. Takes snapshots every minute. Stopped via the operationend command.
@tree.command(name = "operationstart", description = "Begins recording all members that join an operation")
@discord.app_commands.checks.has_any_role("NCO", UCFOfficer, TestOfficer)
async def operationstart(interaction:discord.Interaction):
    await interaction.response.send_message("Operation Started!")
    print("Operation started by: " + str(interaction.user))

    global operationStatus
    operationStatus = True

    while operationStatus == True:
        guild = interaction.guild

        #Adds all members of operation voice channels to the attendees list (memberSet)
        operationVoiceChannels = ['Briefing Room','War Room','Infantry Squad 1','Infantry Squad 2','Steel Legion','Artillery Coolkids','Combat Engineers','Logistics 1','Logistics 2','Facility']
        for channel in operationVoiceChannels:
            await asyncio.sleep(0.5) #Avoids getting rate limited
            for member in discord.utils.get(guild.voice_channels, name=channel).members:
                memberSet.add(member)

        #Waits 1 minute between snapshots as to avoid being rate limited
        await asyncio.sleep(60)
@operationstart.error
async def operationstartError(interaction: discord.Interaction, error: Exception):
    await errorHandling(interaction, error, "NCO/Officer")


#Ends the operation, prints a list of attendees and promotes all attending recruits to private
@tree.command(name = "operationend", description = "Sends a sorted list of operation attendees to put into the report. Also promotes recruits to private") 
@discord.app_commands.checks.has_any_role("NCO", UCFOfficer, TestOfficer)
async def operationend(interaction:discord.Interaction):
    guild = interaction.guild
    await interaction.response.defer()

    #Sets operation to be finished
    global operationStatus
    operationStatus = False

    #Sorts attendees
    sortedList = sortMemberSet(memberSet)
    memberSet.clear()  

    #Creates list of recruits to be promoted
    promoteList = []
    for member in sortedList:
        if member.roles[-1].name == "Recruit":
            promoteList.append(member)
    
    #Prints out attendee list
    recruit = discord.utils.get(guild.roles, name='Recruit')
    private = discord.utils.get(guild.roles, name='Private')
    responseMessage = "**Attendees (" + str(len(sortedList)) + "):**\n\n" + generateReport(sortedList) + "\n" + recruit.mention + " to " + private.mention + ":\n\n" + generateReport(promoteList)
    await interaction.followup.send(responseMessage)
    await interaction.channel.send("```\n" + responseMessage + "\n```")

    #Promotes recruits
    for promotee in promoteList:
        await promotee.edit(nick="+" + promotee.nick)
        await asyncio.sleep(0.5) #Avoids getting rate limited
        await promotee.add_roles(private, reason="After Op Promotion")
        await promotee.remove_roles(recruit, reason="After Op Promotion")   

    print("Operation ended by: " + str(interaction.user))
@operationend.error
async def operationendError(interaction: discord.Interaction, error: Exception):
    await errorHandling(interaction, error, "NCO/Officer")


#Sorts a set by rank, then alphabetical order. Returns a list
def sortMemberSet(memberSet:set):
    #Initialising objects
    sortedList = []
    sortedOfficerList = []
    officerNickList = []
    nickList = []
    memberList = list(memberSet)
    memberDict = {}

    #Adding all members nicknames to a dictionary against their ID. This is so the ID can be reaquirred after sorting by nickname
    for member in memberList:
        if member.bot == False:
            #Checks if member has a nickname. If not, uses real name
            if member.nick:
                nickList.append(member.nick)
                addPair = {member.nick: member}
            else:
                nickList.append(member.name)
                addPair = {member.name: member}
            memberDict.update(addPair)

    #Sorting the list alphabetically, with capitals ignored. This works for sorting enlisted ranks based on nickname alone, but officers need to be sorted by their rank as well as nickname
    nickList.sort(key=str.casefold)

    #Creating a list of all officers
    for nick in nickList:
        splitNick = list(nick)
        if splitNick[0] == "*":
            officerNickList.append(nick)

    #Removing all officers from the nickList, in order to sort them properly
    for officerNick in officerNickList:
        nickList.remove(officerNick)
    
    #Sorting officers by rank, then nickname
    rankList = ["Supreme Commander", "Commander", "Sub-Commander", "Quartermaster", "Facility Master", "Captain", "Lieutenant", "Second Lieutenant", "Officer Cadet", "Sergeant Major", "First Sergeant", "Sergeant", "Assistant Quartermaster", "Assistant Facility Master", "Corporal", "Lance Corporal"]
    for rank in rankList:
        for officerNick in officerNickList:
            officerNickRank = memberDict[officerNick].roles[-1].name
            if officerNickRank == rank:
                sortedOfficerList.append(officerNick)
    
    #Combining sorted enlisted list with sorted officer list
    sortedNickList = sortedOfficerList + nickList 

    #Converting the sorted nickname list into a sorted ID list to be returned
    for nick in sortedNickList:
        sortedList.append(memberDict[nick])
    return sortedList


#Returns a string of list members in proper discord formatting
def generateReport(sortedList: list):
    response = ""
    for member in sortedList:
        response = response + member.mention + "\n"
    return response


#Gets message via converting the string stored inside the file into a message object
async def getMessageFromFile(messageString: str, interaction: discord.Interaction):
    guild = interaction.guild
    messageSplitString = messageString.split(" ") 
    channel = await guild.fetch_channel(messageSplitString[3].lstrip("id="))
    message = await channel.fetch_message(messageSplitString[1].lstrip("id="))
    return message


#Does error handling for when a user does not have the required role to use the command
async def errorHandling(interaction: discord.Interaction, error: Exception, requiredRole: str):
    #Returns message to user if they do not have permission to use the commmand
    if isinstance(error, discord.app_commands.errors.MissingAnyRole):
        await interaction.response.send_message("You are missing the required permissions to use this command. Requires: " + requiredRole)
    #Prints any other error to console, just as they normally would be
    else:
        raise Exception(error)


#Runs the application. Insert token here
client.run('')


"""TODO:
            add leave member robustness
            
            auto assign
            welcome message

            print comfirmation messages for all functions
            logging
            data analysis
    """
