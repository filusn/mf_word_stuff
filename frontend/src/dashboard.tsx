import CloseIcon from "@mui/icons-material/Close";
import DoneIcon from "@mui/icons-material/Done";
import WarningIcon from "@mui/icons-material/Warning";
import { Chip, Container, Typography } from "@mui/material";
import axios from "axios";
import { useEffect, useState } from "react";
import { backend_port } from "./constants";

interface MarkerType {
  label: string;
  status: string | boolean;
}

export interface DashboardProps {
  readonly isSafe: boolean;
  readonly url: string;
}

export default function Dashboard(props: DashboardProps): JSX.Element {
  const { isSafe, url } = props;
  const [markers, setMarkers] = useState<MarkerType[]>();

  useEffect(() => {
    if (!isSafe) setMarkers([{ label: "blacklisted", status: false }]);
    else
      axios
        .post(backend_port + "calculateSiteMarkers", {
          url: url,
        })
        .then((response) => {
          console.log(response.data);
          const result = Object.entries(response.data).map(
            ([key, value]) => ({ label: key, status: value } as MarkerType)
          );
          console.log({ result });
          setMarkers(result);
        })
        .catch((error) => {
          console.error(error);
        });
  }, [isSafe, url]);

  const chipMapping = [
    { status: true, icon: <DoneIcon />, color: "success" },
    { status: "warning", icon: <WarningIcon />, color: "warning" },
    { status: false, icon: <CloseIcon />, color: "error" },
  ];

  return (
    <Container style={{ paddingBottom: "5em" }}>
      <Typography variant="h6" style={{ paddingBottom: "1em" }}>
        How we know this:
      </Typography>
      <div style={{ display: "flex", flexFlow: "column" }}>
        {markers &&
          markers.map((marker) => {
            const chipAttributes = chipMapping.find(
              (chipMap) => chipMap.status === marker.status
            );
            // I was forced by TypeScript to do this, I'm sorry
            const chipColor =
              chipAttributes?.color === "success"
                ? "success"
                : chipAttributes?.color === "warning"
                ? "warning"
                : "error";

            return (
              <div style={{ paddingBottom: "1em" }} key={marker.label}>
                <Chip
                  label={marker.label}
                  icon={chipAttributes?.icon}
                  color={chipColor}
                  style={{ maxWidth: "40em" }}
                  variant="outlined"
                />
              </div>
            );
          })}
      </div>
    </Container>
  );
}

// Alternative design of chips (colored icons)
// const chipColor = chipAttributes?.color === 'success' ? "#a8c256"
//             : chipAttributes?.color === 'warning'
//             ? "#ff9505" : "#ff5a5f"

//             return (
//             <div style={{paddingBottom: '1em'}}>
//                 <Tooltip title={marker.moreInfo}>
//                     <Chip
//                     label={marker.label}
//                     icon={chipAttributes?.icon}
//                     // color={chipColor}
//                     sx={{
//                         [`& .${chipClasses.icon}`]: {
//                         color: chipColor
//                         //   '#21a0a0' // this works
//                         }
//                       }}
//                     style={{maxWidth: '40em'}}
//                     />
//                 </Tooltip>
//             </div>)
