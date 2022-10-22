import discord
import asyncio
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
    addRoleList = ['Recruit','United Colonial Front','Basic Training Not Complete']
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


#Global variable for communicating between votes
voteList = []


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
        
        #Prints message of user to be voted for, and adds emojis for voting
        await interaction.response.send_message(promotee.mention + " to " + rank.mention)
        voteMessage = await interaction.original_response()
        await voteMessage.add_reaction("✅")
        await voteMessage.add_reaction("❌")

        #Adds vote to list to be used in endVoting function
        voteList.append([voteMessage, promotee, rank])

    else:
        await interaction.response.send_message("You do not have the permissions to promote a member to that rank. Requires: Officer")
    

#Promotes members that have been voted on and sends a list of promotees to be put in announcements. Only officers can use this
@tree.command(name = "endvoting", description = "Promotes members that have been voted on and sends a list of promotees. Officer use only")
@discord.app_commands.checks.has_any_role(UCFOfficer, TestOfficer)
async def endvoting(interaction:discord.Interaction):
    guild = interaction.guild
    await interaction.response.defer()

    #Initialising variables
    promoteeList = []
    prefixDict = {'Recruit': '[UCF', 'Private': '+[UCF', 'Veteran': '++[UCF', 'Legionnaire': '+++[UCF',
                  'Pioneer': '*[UCF☆', 'Lance Corporal': '*[UCF☆', 'Corporal': '*[UCF☆', 'Assistant Quartermaster': '**[UCF☆', 'Sergeant': '*[UCF☆', 'First Sergeant': '*[UCF☆', 'Sergeant Major': '*[UCF☆',
                  'Officer Cadet': '**[UCF★', 'Second Lieutenant': '**[UCF★', 'Lieutenant': '**[UCF★', 'Captain': '**[UCF★', 'Commodore': '**[UCF★', 'Quartermaster': '**[UCF★',
                  'Sub-Commander': '***[UCF★', 'Commander': '***[UCF★', 'Supreme Commander': '***[UCF★'}

    #Setting nickname of sucsessful promotees. Adds promotees to list for printing
    for vote in voteList:
        #Refreshing vote message so the bot knows about reactions taken place after initial recording of the message. Doesnt update if message was deleted
        try:
            vote[0] = await vote[0].fetch()
        except:
            print("Failed due to message being deleted")    #TODO: This doesnt stop the error however

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

    #Prints list of promotees, with ranks seperating themm
    promoteeDict = dict(promoteeList)
    sortedList = sortMemberSet(set([row[0] for row in promoteeList]))
    response = ""
    previousRank = ''
    for promotee in sortedList:
        if not promoteeDict[promotee] == previousRank:
            response = response + "\n" + promoteeDict[promotee].mention + "\n\n"

        response = response + promotee.mention + "\n"
        previousRank = promoteeDict[promotee]

    await interaction.followup.send(response)

    #Updates roles
    for promotee in promoteeList:
        #Removes previous rank, adds new
        await promotee[0].remove_roles(promotee[0].roles[-1], reason="Promoted via vote by UCF Bot")
        await promotee[0].add_roles(promotee[1], reason="Promoted via vote by UCF Bot")

        #Gives NCO role
        if promotee[1].name == 'Lance Corporal':
            await promotee[0].add_roles(discord.utils.get(guild.roles, name='NCO'), reason="Promoted via vote by UCF Bot")
        #Gives Officer role
        if promotee[1].name == 'Officer Cadet':
            await promotee[0].add_roles(discord.utils.get(guild.roles, name='Officer'), reason="Promoted via vote by UCF Bot")
            await promotee[0].remove_roles(discord.utils.get(guild.roles, name='NCO'), reason="Promoted via vote by UCF Bot")
            
    #Clears list
    voteList.clear()

    #Updates rank structure
    await editRankStructure(interaction)
    

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


#Edits the rank structure message. Can be called manually using above function, or can be called automatically
async def editRankStructure(interaction):
    guild = interaction.guild

    #Initialising variables
    message = ""

    #Reads from rank structure file
    with open('rank_structure_message.txt', 'r') as file:
        #Gets message via converting the string stored inside the file into a message object
        messageString = file.readline()
        messageSplitString = messageString.split(" ") 
        channel = await guild.fetch_channel(messageSplitString[3].lstrip("id="))
        message = await channel.fetch_message(messageSplitString[1].lstrip("id="))

    #Updates message
    await message.edit(content = await generateRankStructure(interaction))


#Generates the rank structure message
async def generateRankStructure(interaction):
    guild = interaction.guild

    #Initialising variables
    rankStructure = ""
    rankList = ["Supreme Commander", "Commander", "Sub-Commander", "Quartermaster", "Commodore", "Captain", "Lieutenant", "Second Lieutenant", "Officer Cadet", "Sergeant Major", "First Sergeant", "Sergeant", "Assistant Quartermaster", "Corporal", "Lance Corporal"]
    capacityDict = {'Pioneer': '*N/A*', 'Lance Corporal': '*8 Slots*', 'Corporal': '*6 Slots*', 'Assistant Quartermaster': '*4 Slots*', 'Sergeant': '*2 Slots*', 'First Sergeant': '*2 Slots*', 'Sergeant Major': '*1 Slot*',
                   'Officer Cadet': '*Trial Rank*', 'Second Lieutenant': '*2 Slots*', 'Lieutenant': '*2 Slots*', 'Captain': '*2 Slots*', 'Commodore': '*1 Slot*', 'Quartermaster': '*1 Slot*',
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

    #Gets training voice members and prints them out
    traineeSet = set()
    trainingVoice = discord.utils.get(guild.voice_channels, name='Training-VC')
    for trainee in trainingVoice.members:
        traineeSet.add(trainee)
    traineeSet.remove(interaction.user) #Removes training host from set
    sortedList = sortMemberSet(traineeSet)
    await interaction.followup.send(generateReport(sortedList))

    #Adds and removes roles
    trainingComplete = discord.utils.get(guild.roles, name='Basic Training Complete')
    trainingNotComplete = discord.utils.get(guild.roles, name='Basic Training Not Complete')
    for trainee in sortedList:
        await asyncio.sleep(1) #Avoids getting rate limited
        await trainee.add_roles(trainingComplete, reason="Added by UCF Bot")
        await trainee.remove_roles(trainingNotComplete, reason="Removed by UCF Bot")

    print("Basic training complete for: " + str(sortedList) + " by: " + str(interaction.user))


#Takes a snapshot of a specifed voice channel and prints it out
@tree.command(name = "voicesnapshot", description = "Prints a list of all members currently in a specified voice channel")
@discord.app_commands.checks.has_any_role("NCO", UCFOfficer, TestOfficer)
async def voicesnapshot(interaction:discord.Interaction, voicechannel:discord.VoiceChannel):
    guild = interaction.guild
    await interaction.response.defer()

    #Gets voice members and prints them out
    voiceSet = set()
    for i in voicechannel.members:
        voiceSet.add(i)
    sortedList = sortMemberSet(voiceSet)
    await interaction.followup.send(generateReport(sortedList))

    print("Snapshot taken for channel: " + str(voicechannel) + " by: " + str(interaction.user))


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
            await asyncio.sleep(1) #Avoids getting rate limited
            for member in discord.utils.get(guild.voice_channels, name=channel).members:
                memberSet.add(member)

        #Waits 1 minute between snapshots as to avoid being rate limited
        await asyncio.sleep(60)


#Ends the operation, prints a list of attendees and promotes all attending recruits to private
@tree.command(name = "operationend", description = "Sends a sorted list of operation attendees to put into the report. Also promotes recruits to private") 
@discord.app_commands.checks.has_any_role("NCO", UCFOfficer, TestOfficer)
async def operationend(interaction:discord.Interaction):
    await interaction.response.defer()

    #Sets operation to be finished
    global operationStatus
    operationStatus = False

    #Prints out attendee list
    sortedList = sortMemberSet(memberSet)
    await interaction.followup.send("**Attendees (" + str(len(sortedList)) + "):\n\n**" + generateReport(sortedList))
    memberSet.clear()     

    print("Operation ended by: " + str(interaction.user))


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
        if member.bot ==  False:
            nickList.append(member.nick)
            addPair = {member.nick: member}
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
    rankList = ["Supreme Commander", "Commander", "Sub-Commander", "Quartermaster", "Commodore", "Captain", "Lieutenant", "Second Lieutenant", "Officer Cadet", "Sergeant Major", "First Sergeant", "Sergeant", "Assistant Quartermaster", "Corporal", "Lance Corporal"]
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


#Runs the application. Insert token here
client.run('')


"""TODO:
            operation end promoting

            auto assign
            welcome message
            let user add rank roles to avoid having to touch the code

            error handling
            robustness

            print comfirmation messages for all functions
            logging
            data analysis
    """
