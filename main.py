import socket
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView

# Set the server IP address and port number
SERVER_IP = "192.168.0.109"  # Replace with the server's IP address
SERVER_PORT = 80

class ClientGUI(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        self.file_chooser = FileChooserListView()
        layout.add_widget(self.file_chooser)
        
        send_button = Button(text="Send Files")
        send_button.bind(on_release=self.send_files)
        layout.add_widget(send_button)
        
        receive_button = Button(text="Receive Files")
        receive_button.bind(on_release=self.receive_files)
        layout.add_widget(receive_button)
        
        return layout
    
    def send_files(self, instance):
        file_list = self.file_chooser.selection
        
        if file_list:
            Thread(target=self.send_files_thread, args=(file_list,)).start()
    
    def send_files_thread(self, file_list):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_IP, SERVER_PORT))
            
            # Send the number of files to the server
            client_socket.send(str(len(file_list)).encode())
            
            for file_path in file_list:
                filename = os.path.basename(file_path)
                
                # Send each filename to the server
                client_socket.send(filename.encode())
                
                # Send the file data to the server
                with open(file_path, "rb") as file:
                    filedata = file.read(1024)
                    while filedata:
                        client_socket.send(filedata)
                        filedata = file.read(1024)
            
                print("Sent", filename)
        
        print("All files sent successfully.")
    
    def receive_files(self, instance):
        Thread(target=self.receive_files_thread).start()
    
    def receive_files_thread(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_IP, SERVER_PORT))
            
            # Send the number of files to receive (0 indicates receive all)
            client_socket.send(b"0")
            
            while True:
                filename = client_socket.recv(1024).decode()
                
                if not filename:
                    break
                
                filedata = client_socket.recv(1024)
                
                with open(filename, "wb") as file:
                    while filedata:
                        file.write(filedata)
                        filedata = client_socket.recv(1024)
                
                print("Received", filename)
        
        print("All files received.")

if __name__ == '__main__':
    ClientGUI().run(android=True)
