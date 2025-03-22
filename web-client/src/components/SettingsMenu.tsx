import React, { useEffect, useState } from "react";
import axios from "axios";

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";

const SettingsMenu = () => {
  const fastURL = "http://192.168.141.1:8000/";

  const [ra, setRa] = useState("");
  const [dec, setDec] = useState("");

  const handleManualCalibrateClick = async () => {
    if (!ra || !dec) {
      alert("Please enter both RA and DEC values.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("ra", ra);
      formData.append("dec", dec);

      const response = await axios.post(fastURL + "api/calibrate/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      alert("Calibration successful!");
    } 
    catch (error) {
      console.error("Error during calibration:", error);
      alert("Calibration failed.");
    }
  };

  return (
    <div>
      <Card>
        <CardHeader />
        <CardContent className="flex justify-center gap-x-2">
          <div className="grid w-full max-w-sm gap-2">
            <Label >Manual Calibration</Label>
            <Input
              type="text"
              id="ra"
              placeholder="Enter Right Ascension (RA)"
              value={ra}
              onChange={(e) => setRa(e.target.value)}
            />
            <Input
              type="text"
              id="dec"
              placeholder="Enter Declination (DEC)"
              value={dec}
              onChange={(e) => setDec(e.target.value)}
            />
          </div>
        </CardContent>
        <CardContent className="flex justify-center gap-x-2">
          <Button onClick={handleManualCalibrateClick} className="w-40 p-2">
            CALIBRATE
          </Button>
        </CardContent>
        <CardFooter />
      </Card>
    </div>
  );
};

export default SettingsMenu;