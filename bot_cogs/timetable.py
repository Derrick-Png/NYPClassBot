from typing import Union
import asyncio
import re
import time
import os
import traceback
from datetime import datetime
import discord
from discord.ext import commands, tasks
import shutil
import requests
from bot_cogs.base.base_cog import BaseCog
from modules import dataprocess, upscaler, timetableconverter, database
class TimeTable(BaseCog):
    @commands.group()
    # @commands.guild_only()
    async def timetable(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help("timetable")

    @timetable.command(usage="<name>")
    async def add(self, ctx: commands.Context, name: str):
        author: Union[discord.User, discord.Member] = ctx.author
        try:
            await author.send(
                "Please upload an image of the timetable from the NYP website."
            )
        except Exception as error:
            if isinstance(error, discord.Forbidden):
                await ctx.send(
                    "{} please turn on your DMs and try again.".format(author.mention)
                )
            else:
                await ctx.send(
                    "{} I was unable to send you a DM. Error: {}".format(
                        author.mention, error
                    )
                )
            # stop function from running since DM could not be sent
            return

        if ctx.channel.type != discord.ChannelType.private:
            await ctx.send("You have been prompted in your DMs.")

        def check(msg: discord.Message):
            return msg.author == author and msg.channel.type == discord.ChannelType.private

        try:
            await author.send("You have 10 seconds to send an image.")
            msg: discord.Message = await self.bot.wait_for(
                "message", check=check, timeout=10
            )
        except asyncio.TimeoutError:
            await author.send(
                "You did not send an image on time, the prompt has been cancelled."
            )
            return
        guildId = ctx.guild.id
        guildId = f"{guildId}_{name}"
        # paths for input and output
        imagePath = os.path.join(os.getcwd(), f"images/{guildId}.png")
        excelPath = os.path.join(os.getcwd(), f"excel/{guildId}.xlsx")
        try:
            url = msg.attachments[0].url
        except IndexError:
            print("Invalid image.")
            await author.send("Invalid image.")
            return


        if url[0:26] == "https://cdn.discordapp.com":
            await author.send("Processing image...")
            r = requests.get(url, stream=True)
            with open(imagePath, "wb") as out_file:
                print("saving image: " + imagePath)
                shutil.copyfileobj(r.raw, out_file)
        await author.send("File saved, upscaling now.")
        #############################################
        upscaler.upscale(imagePath, guildId)
        await author.send("Upscaling finished, converting to excel now.")
        ###############converting xlxs#################
        try:
            timetableconverter.readfile(imagePath, guildId)
        except Exception as e:
            print(e.__traceback__)
        await author.send("File converted to excel, cleaning file.")
        ###############cleaning xlxs#################
        array_of_entries = (dataprocess.cleanData(excelPath, guildId))[0]
        await author.send("File has been cleaned, adding to database.")
        #############inserting to db#################
        db = database.Db(f"{guildId}")
        await author.send("Database has been created.")
        db.insertManyEntry(array_of_entries)
        await author.send("Collection has been inserted.")
        try:
            os.remove(imagePath)
            os.remove(excelPath)
        except Exception as e:
            print(e.__traceback__)

            


    #     def check(msg: discord.Message):
    #         return (
    #             msg.author == author
    #             and msg.channel.type == discord.ChannelType.private
    #             and len(msg.attachments) > 0
    #             and re.search(".+[.](.+)", msg.attachments[0].filename).group(1) in valid_image_extensions
    #         )

    #     try:
    #         received_msg: discord.Message = await self.bot.wait_for("message", check=check, timeout=30)
    #     except asyncio.TimeoutError:
    #         await author.send("You did not send an image on time, the prompt has been cancelled.")
    #         return

    #     attachment = received_msg.attachments[0]
    #     progress_message = await author.send("Saving the image...")

    #     try:
    #         attachment_path = os.path.join(os.getcwd(), "Images/{}.png".format(attachment.id))
    #         attachment_size = await attachment.save(attachment_path)
    #     except Exception as error:
    #         await author.send(
    #             "An unexpected error has occurred. Please try again. (error: {})"
    #             .format(error)
    #         )
    #         return

    #     await progress_message.edit(content="Image saved! Size: {}B".format(attachment_size))

    #     convert_message = await author.send("Converting to data...")
    #     start_time = time.time()
    #     converter = TimeTableConverter(image = attachment_path, id=attachment.id, debug=False)
    #     # ^debug param toggles saving of df to pickle for debugging later

    #     last_tracked = 0
    #     last_percentage = 0

    #     # every 3 seconds, update progress percentage
    #     # progress is determined by convert.progress which is incremented
    #     # in the for loop in converter.read_file() that converts the text from the image
    #     @tasks.loop(seconds=3)
    #     async def edit_msg_loop():
    #         nonlocal last_tracked
    #         if last_tracked == 0:
    #             last_tracked = time.time()

    #         time_since_last_tracked = time.time() - last_tracked
    #         current_percentage = converter.progress
    #         percentage_gain = current_percentage - last_percentage

    #         if time_since_last_tracked > 0 and percentage_gain > 0:
    #             rate = percentage_gain / time_since_last_tracked
    #             time_left = (1 - current_percentage) / rate
    #             time_left_str = str(round(time_left, 2)) + "s"
    #         else:
    #             time_left_str = "N/A"

    #         await convert_message.edit(
    #             content=(
    #                 "Converting to data... {:.2f}% (est. time left: {})"
    #                 .format(converter.progress * 100, time_left_str)
    #             )
    #         )

    #     # once loop is over, set final message of time taken
    #     @edit_msg_loop.after_loop
    #     async def edit_msg_end():
    #         save_duration = time.time() - start_time
    #         await convert_message.edit(content="Converted to data! Took {:.3f}s".format(save_duration))

    #     # this runs converter.readfile "concurrently" on a separate thread
    #     # making convert.readfile an async func (coroutine) does not actually
    #     # make it run on a separate thread since it does not have an await
    #     async def read():
    #         loop = asyncio.get_running_loop()
    #         return await loop.run_in_executor(None, converter.readfile, attachment_path)

    #     try:
    #         edit_msg_loop.start()
    #         dataframe = await read()
    #         edit_msg_loop.cancel()
    #     except Exception as error:
    #         traceback.print_tb(error.__traceback__)
    #         await author.send("Unable to convert to data! Please try again. {}".format(error))
    #         return
    #     finally:
    #         os.remove(attachment_path)

    #     try:
    #         clean_data, tabulated_data = dataprocess.cleanData(dataframe)
    #     except Exception as error:
    #         traceback.print_tb(error.__traceback__)
    #         await author.send("Unable to clean data! Please try again. {}".format(error))
    #         return

    #     await author.send("```\n{}\n```".format(tabulated_data[:900]))

    @timetable.command(usage="<name>", enabled=True)
    async def remove(self, ctx: commands.Context, name: str):
        guildId = ctx.guild.id
        guildcollections = [x.split("_")[1] for x in database.db.list_collection_names() if x.startswith(str(guildId))]
        if name not in guildcollections:
            await ctx.send("Timetable does not exist.")
        else:
            removal = database.db[f"{guildId}_{name}"]
            removal.drop()
            await ctx.send(f"{name} has been removed")

    @timetable.command(usage="peepeepoopoo", enabled=True)
    async def list(self, ctx: commands.Context):
        guildId = ctx.guild.id
        message = [x for x in database.db.list_collection_names() if x.startswith(str(guildId))]
        output = ""
        for x in range(len(message)):
            y = message[x].split("_")[1]
            output += f"{x+1}. {y}\n" 
        await ctx.send(output)
    


def setup(bot: commands.Bot):
    bot.add_cog(TimeTable(bot))
