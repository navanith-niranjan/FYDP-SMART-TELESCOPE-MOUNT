import { useState, useEffect } from "react";
import axios from "axios";

import Calibrate from "./components/Calibrate";
import Catalog from "./components/Catalog";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DraftingCompass, Locate} from "lucide-react";

const App = () => {
  // 192.168.141.1

  const fastURL = "http://localhost:8000/"

  const [calibrateMessage, setCalibrateMessage] = useState("Not Calibrated")

  useEffect(() => {
      const fetchData = async () => {
          try {
              const response = await axios.get(fastURL);
          } catch (error) {
              console.error("Error fetching data:", error);
          }
      };

      fetchData();
  }, []);

  const handleImageUpload = async (imageFile: File | null) => {
    if (imageFile) {
      const formData = new FormData();
      formData.append("file", imageFile, imageFile.name);

        const response = await axios.post(fastURL + "api/upload/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        if (response.data.ra & response.data.dec) {
          setCalibrateMessage(response.data.message + " RA: " + response.data.ra + " DEC: " + response.data.dec)
        }
        else {
          setCalibrateMessage(response.data.message)
        }
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen">
      <Tabs defaultValue="calibrate" className="w-[20vw]">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="calibrate">< DraftingCompass /></TabsTrigger>
          <TabsTrigger value="locate">< Locate /></TabsTrigger>
        </TabsList>
        <TabsContent value="calibrate">
          <Calibrate onImageUpload={handleImageUpload} onMessage={setCalibrateMessage} message={calibrateMessage}/>
        </TabsContent>
        <TabsContent value="locate">
          <Catalog />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default App
