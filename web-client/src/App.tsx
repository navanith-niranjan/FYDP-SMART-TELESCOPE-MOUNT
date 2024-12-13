import { useState, useEffect } from "react";
import axios from "axios";

import Calibrate from "./components/Calibrate";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DraftingCompass, Locate } from "lucide-react";
import Catalog from "./components/Catalog";

const App = () => {
  const [message, setMessage] = useState("");

  useEffect(() => {
      const fetchData = async () => {
          try {
              const response = await axios.get("http://192.168.141.1:8000/");
              setMessage(response.data.message);
          } catch (error) {
              console.error("Error fetching data:", error);
          }
      };

      fetchData();
  }, []);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <Tabs defaultValue="calibrate" className="w-[20vw]">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="calibrate">< DraftingCompass /></TabsTrigger>
          <TabsTrigger value="locate">< Locate /></TabsTrigger>
        </TabsList>
        <TabsContent value="calibrate">
          <Calibrate />
        </TabsContent>
        <TabsContent value="locate">
          <Catalog />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default App
