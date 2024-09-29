import DangerousIcon from '@mui/icons-material/Dangerous';
import LocalPoliceIcon from '@mui/icons-material/LocalPolice';
import { Container, LinearProgress, Typography } from '@mui/material';

import { theme } from './theme';
import { isValidUrl } from './url-paste-bar';

export interface ResultContainerProps {
  readonly isSafe: boolean;
}

export default function ResultContainer(props: ResultContainerProps): JSX.Element {
    const {isSafe} = props

    const message = isSafe
    return <Container style={{paddingBottom: '3em'}}>
                    <Typography
                variant="h4"
                style={{
                    textAlign: 'center',
                    paddingBottom: '1em',
                    fontWeight: 'bold',
                }}
            >
                Transcription:
            </Typography>
        <div style={{display: 'flex', flexFlow: 'row', justifyContent: 'center', paddingBottom: '1em'}}>

        <Typography variant="h6" style={{color: isSafe ? theme.palette.success.main : theme.palette.error.main, textAlign: 'justify',}}>{message}</Typography>
        </div>
      <Typography variant="h6" style={{ paddingBottom: "1em" }}>
      </Typography>
      <div
        style={{ display: "flex", flexFlow: "row", justifyContent: "center" }}
      >

      </div>
    </Container>
}
