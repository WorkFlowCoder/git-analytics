import "./InfoTooltip.css";

type Props = {
  title: string;
  text: string;
  pins: string[];
};

export default function InfoTooltip({ title, text, pins }: Props) {
  return (
    <div className="info-wrapper">
  <div className="info-icon">i</div>

  <div className="info-tooltip">
    <div className="info-title">{title}</div>
    <div className="info-text">{text}</div>

    {pins?.length > 0 && (
        <div className="info-pins">
            {pins.map((pin, index) => (
                <div key={index} className="info-pin">
                    <span className="pin-dot" />
                    <span>{pin}</span>
                </div>
            ))}
        </div>
    )}
  </div>
</div>
  );
}