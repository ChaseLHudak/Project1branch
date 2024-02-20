import tkinter as tk
import pygubu
from tkinter import messagebox
from typing import Dict, List
from supabase_manager import supabase, insert_user

# Make build_ui_instance a global variable to hold the pygubu.Builder instance
build_ui_instance: pygubu.Builder = pygubu.Builder()


def on_continue_clicked(root: tk.Tk, users, input_ids) -> None:
    # Initialize lists to store user data
    user_data = []

    # Iterate over input IDs to retrieve user information
    for input_id, field_name in input_ids.items():
        entry = build_ui_instance.get_object(input_id)
        if entry:
            user_data.append((field_name.split("_")[0], entry.get()))

    # Validate user data here if needed
    if len(user_data) < 6:
        messagebox.showerror("Error", "Not enough user information provided.")
        return

    # Insert user data into Supabase table
    for i in range(0, len(user_data), 3):
        username = user_data[i][1]
        user_id = user_data[i + 1][1]

        # Convert user_id to int (assuming user_id should be an integer)
        try:
            user_id = int(user_id)
        except ValueError:
            messagebox.showerror("Error", "User ID must be a valid number.")
            return

        insert_user("username", 13)

    # Notify user of successful insertion
    messagebox.showinfo("Success", "User information inserted successfully.")


def build_ui(root: tk.Tk, users: dict) -> None:
    builder: pygubu.Builder = pygubu.Builder()
    try:
        builder.add_from_file("ui/player_interface.ui")
    except:
        builder.add_from_file("../ui/player_interface.ui")

    main_frame: tk.Frame = builder.get_object("master", root)
    main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    red_frame: tk.Frame = builder.get_object("red_team", main_frame)
    blue_frame: tk.Frame = builder.get_object("blue_team", main_frame)

    input_ids: Dict[int, str] = {}
    fields: List[str] = {
        "red_equipment_id_",
        "red_user_id_",
        "red_username_",
        "blue_equipment_id_",
        "blue_user_id_",
        "blue_username_"
    }

    for i in range(1, 16):
        for field in fields:
            entry = builder.get_object(f"{field}{i}",
                                       red_frame if "red" in field else blue_frame)
            input_ids[entry.winfo_id()] = f"{field}{i}"
            entry.bind("<Return>", lambda event, entry=entry: autofill_user_id(entry))

    builder.get_object("submit").configure(command=lambda: on_continue_clicked(root, users, input_ids))


def autofill_user_id(entry):
    username = entry.get().strip()
    if username:
        try:
            # Get the parent frame
            parent_frame = entry.master
            while parent_frame.winfo_name() not in {"red_team", "blue_team"}:
                parent_frame = parent_frame.master

            # Get the corresponding user ID entry widget
            user_id_entry = parent_frame.nametowidget(entry.winfo_name().replace("username", "user_id"))
            if user_id_entry:
                # Query Supabase to find user ID based on username
                query = supabase.table("users").select("user_id").eq("username", username)
                response = query.execute()
                print("Response from Supabase:", response)  # Debugging statement

                # Check if response contains data and retrieve user ID
                if hasattr(response, "data") and len(response.data) > 0:
                    user_id = response.data[0]["user_id"]
                    print("Retrieved user ID:", user_id)  # Debugging statement
                    user_id_entry.delete(0, tk.END)  # Clear existing content
                    user_id_entry.insert(0, str(user_id))
                else:
                    print("No user ID data found in response.")  # Debugging statement
            else:
                print("User ID entry widget not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
